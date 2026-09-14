import os
import json
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

class FinancialDecisionEngine:
    def __init__(self, data_dir="dataset"):
        self.data_dir = data_dir
        self.load_data()

    def load_data(self):
        self.profiles = pd.read_csv(os.path.join(self.data_dir, "financial_profiles.csv")).set_index("user_id")
        self.events = pd.read_csv(os.path.join(self.data_dir, "financial_events.csv"))
        self.options = pd.read_csv(os.path.join(self.data_dir, "request_payment_options.csv"))
        self.messages = pd.read_csv(os.path.join(self.data_dir, "messages.csv"))

        img_json = os.path.join(self.data_dir, "extracted_image_amounts.json")
        if os.path.exists(img_json):
            with open(img_json, "r", encoding="utf-8") as f:
                extracted = json.load(f)
                for eid, item in extracted.items():
                    m = self.events["event_id"] == eid
                    self.events.loc[m, "amount"] = item["amount"]

        self.events["event_dt"] = pd.to_datetime(self.events["event_date"])
        self.events["settle_dt"] = pd.to_datetime(self.events["settlement_date"])

    def add_months(self, d, months):
        new_m = d.month + months
        new_y = d.year + (new_m - 1) // 12
        new_m = (new_m - 1) % 12 + 1
        max_d = calendar.monthrange(new_y, new_m)[1]
        return datetime(new_y, new_m, min(d.day, max_d))

    def evaluate_request(self, req_row):
        req_id = req_row["request_id"]
        user_id = req_row["user_id"]
        req_dt = datetime.strptime(str(req_row["request_date"]), "%Y-%m-%d")
        req_amount = float(req_row["requested_amount"])
        target_dt = datetime.strptime(str(req_row["desired_completion_date"]), "%Y-%m-%d")
        allows_partial = str(req_row.get("allows_partial_payment", "")).lower() == "true"

        prof = self.profiles.loc[user_id]
        home_curr = prof["home_currency"]
        start_bal = float(prof["current_available_balance"])
        min_bal = float(prof["minimum_balance_to_keep"])
        considered = [m.strip() for m in str(prof.get("payment_methods_user_will_consider", "")).split("|")]
        max_inst = prof.get("max_installment_months")
        max_inst = float(max_inst) if pd.notna(max_inst) else None

        will_stop = [c.strip() for c in str(prof.get("expense_categories_user_is_willing_to_stop", "")).split("|") if c.strip()]
        will_reduce = [c.strip() for c in str(prof.get("expense_categories_user_is_willing_to_reduce", "")).split("|") if c.strip()]

        u_ev = self.events[self.events["user_id"] == user_id].copy()

        # 1. 90-Day Simulation Array
        daily_net = [0.0] * 91 

        # Pending debits hit immediately
        pending = u_ev[(u_ev["status"] == "pending") & (u_ev["direction"] == "debit")]
        pending_debit_sum = float(pending["amount"].sum()) if len(pending) > 0 else 0.0
        daily_net[0] -= pending_debit_sum

        # Confirmed / Scheduled salary from events
        salaries = u_ev[(u_ev["direction"] == "credit") & 
                        (u_ev["status"].isin(["settled", "scheduled"])) & 
                        (u_ev["category"].str.contains("salary|payroll", case=False, na=False))].sort_values("settle_dt")
        
        salary_amt = 0.0
        salary_day = 15
        if len(salaries) > 0:
            last_sal = salaries.iloc[-1]
            salary_amt = float(last_sal["amount"])
            if pd.notna(last_sal["settle_dt"]):
                salary_day = last_sal["settle_dt"].day
            elif pd.notna(last_sal["event_dt"]):
                salary_day = last_sal["event_dt"].day

        # BULLETPROOF REGEX FOR MESSAGES (Ignores EMP-xxxx and Dates!)
        for _, m in self.messages[self.messages["user_id"] == user_id].iterrows():
            m_text = str(m.get("message_text", ""))
            if "payroll" in m_text.lower() or "salary" in m_text.lower():
                # Extract amount following currency or keywords (e.g. "EUR 1037.52" or "salary will be EUR 1661")
                amt_match = re.search(r"(?:EUR|USD|INR|IDR|ZAR|pay is|salary is|salary will be)\s*(?:EUR|USD|INR|IDR|ZAR)?\s*([\d,]+(?:\.\d+)?)", m_text, re.IGNORECASE)
                if amt_match:
                    try:
                        clean_num = amt_match.group(1).replace(",", "")
                        parsed_val = float(clean_num)
                        if parsed_val > 10.0:  # Must be real salary, not single digits
                            salary_amt = parsed_val
                    except: pass
                
                # Extract confirmed credit date if present (e.g. "confirmed credit date is 2026-01-15")
                date_match = re.search(r"\b(202\d-\d{2}-\d{2})\b", m_text)
                if date_match:
                    try:
                        salary_day = datetime.strptime(date_match.group(1), "%Y-%m-%d").day
                    except: pass

        # Project salary over 90 days
        future_salary_dates = []
        for i in range(4):
            try:
                s_dt = datetime(req_dt.year, req_dt.month, min(salary_day, 28))
                s_dt = self.add_months(s_dt, i)
                days_ahead = (s_dt - req_dt).days
                if 0 <= days_ahead <= 90:
                    daily_net[days_ahead] += salary_amt
                    future_salary_dates.append(s_dt)
            except: pass

        # Explicit scheduled future debits
        sched_debits = u_ev[(u_ev["direction"] == "debit") & (u_ev["status"] == "scheduled")]
        for _, s_ev in sched_debits.iterrows():
            s_date = s_ev["settle_dt"] if pd.notna(s_ev["settle_dt"]) else s_ev["event_dt"]
            if pd.notna(s_date):
                d_ahead = (s_date - req_dt).days
                if 0 <= d_ahead <= 90:
                    daily_net[d_ahead] -= float(s_ev["amount"])

        # Project Only True Recurring Debits (Subscriptions, Rent, Utilities, Insurance)
        recurring_past = u_ev[(u_ev["event_dt"] >= req_dt - timedelta(days=35)) & 
                             (u_ev["event_dt"] < req_dt) & 
                             (u_ev["direction"] == "debit") & 
                             (u_ev["status"] == "settled") & 
                             ((u_ev["event_type"] == "subscription") | 
                              (u_ev["category"].str.contains("rent|util|insur", case=False, na=False)))]

        flexible_savings = 0.0
        spending_changes_list = []
        seen_eid = set()

        for _, ev in recurring_past.iterrows():
            amt = float(ev["amount"])
            cat = str(ev.get("category", ""))
            flex = str(ev.get("flexibility", ""))
            eid = ev["event_id"]
            min_allow = float(ev.get("minimum_allowed_amount", 0.0)) if pd.notna(ev.get("minimum_allowed_amount")) else 0.0

            for i in range(4):
                try:
                    p_dt = self.add_months(ev["event_dt"], i)
                    days_ahead = (p_dt - req_dt).days
                    if 0 <= days_ahead <= 90:
                        daily_net[days_ahead] -= amt
                except: pass

            if eid not in seen_eid and len(spending_changes_list) < 3:
                if cat in will_stop and flex in ["stoppable", "reducible_or_stoppable"]:
                    spending_changes_list.append(f"stop:{eid}")
                    flexible_savings += amt
                    seen_eid.add(eid)
                elif cat in will_reduce and flex in ["reducible", "reducible_or_stoppable"] and amt > min_allow:
                    spending_changes_list.append(f"reduce_to:{eid}:{min_allow:.2f}".rstrip('0').rstrip('.'))
                    flexible_savings += (amt - min_allow)
                    seen_eid.add(eid)

        # 2. Simulate Daily Balances
        balances = [0.0] * 91
        curr_bal = start_bal
        for i in range(91):
            curr_bal += daily_net[i]
            balances[i] = curr_bal

        min_bal_90 = min(balances)
        uncapped_safe_today = max(0.0, min_bal_90 - min_bal)
        amount_safe_to_pay = min(req_amount, uncapped_safe_today)

        # 3. Earliest Date for Single Full Payment
        earliest_full_date = ""
        if uncapped_safe_today >= req_amount:
            earliest_full_date = req_dt.strftime("%Y-%m-%d")
        else:
            for d in range(1, 91):
                if min(balances[d:]) - req_amount >= min_bal:
                    earliest_full_date = (req_dt + timedelta(days=d)).strftime("%Y-%m-%d")
                    break

        # 4. Decisions
        status = "not_affordable"
        method = "not_recommended"
        plan = "none"
        changes = "none"
        exp = ""

        # Can pay full today without changes?
        if uncapped_safe_today >= req_amount and "full_payment" in considered:
            status = "affordable_now"
            method = "full_payment"
            plan = f"{req_dt.strftime('%Y-%m-%d')}:{int(req_amount) if req_amount.is_integer() else req_amount:.2f}".rstrip('0').rstrip('.')
            earliest_full_date = req_dt.strftime("%Y-%m-%d")
            exp = f"Pay {home_curr} {req_amount:,.2f} today. This leaves at least {home_curr} {min_bal:,.2f} available over the next 90 days."

        # Can pay full today WITH spending changes?
        elif (uncapped_safe_today + flexible_savings) >= req_amount and "full_payment" in considered and req_dt <= target_dt:
            status = "affordable_with_plan"
            method = "full_payment"
            plan = f"{req_dt.strftime('%Y-%m-%d')}:{int(req_amount) if req_amount.is_integer() else req_amount:.2f}".rstrip('0').rstrip('.')
            changes = "|".join(spending_changes_list[:2]) if spending_changes_list else "none"
            exp = f"Make required spending changes ({changes}) and pay {home_curr} {req_amount:,.2f} today."

        else:
            eligible_plans = []

            # Partial payment (Priority with 0 fee)
            if allows_partial and "partial_payment" in considered and 0 < amount_safe_to_pay < req_amount and earliest_full_date:
                e_dt = datetime.strptime(earliest_full_date, "%Y-%m-%d")
                if e_dt <= target_dt:
                    rem = req_amount - amount_safe_to_pay
                    p_str = f"{req_dt.strftime('%Y-%m-%d')}:{amount_safe_to_pay:.2f}|{earliest_full_date}:{rem:.2f}"
                    eligible_plans.append({
                        "id": 0, "method": "partial_payment", "plan": p_str, "total": req_amount,
                        "first": req_dt, "num": 2, "req_sp": False, "chg": "none",
                        "exp": f"Pay {home_curr} {amount_safe_to_pay:,.2f} today and remaining {home_curr} {rem:,.2f} on {earliest_full_date}."
                    })

            # Installment options
            req_opts = self.options[self.options["request_id"] == req_id]
            for _, opt in req_opts.iterrows():
                opt_id = int(str(opt["payment_option_id"]).replace("payment_option_", ""))
                p_method = opt["payment_method"]
                p_amt = float(opt["payment_amount"])
                num_p = int(opt["number_of_payments"])
                first_dt = datetime.strptime(str(opt["first_payment_date"]), "%Y-%m-%d")
                freq_days = float(opt.get("payment_frequency_days", 30.0))
                if pd.isna(freq_days): freq_days = 30.0
                total = float(opt["total_payable_amount"])

                if p_method not in considered: continue
                if max_inst and ((num_p * freq_days) / 30.0) > (max_inst + 0.1): continue
                
                dates = [first_dt + timedelta(days=int(i * freq_days)) for i in range(num_p)]
                if dates[-1] > target_dt: continue

                if p_amt <= (uncapped_safe_today + flexible_savings):
                    needs_sp = (p_amt > uncapped_safe_today)
                    chg = "|".join(spending_changes_list[:2]) if (needs_sp and spending_changes_list) else "none"
                    plan_str = "|".join([f"{d.strftime('%Y-%m-%d')}:{p_amt:.2f}".rstrip('0').rstrip('.') if p_amt.is_integer() else f"{d.strftime('%Y-%m-%d')}:{p_amt:.2f}" for d in dates])
                    eligible_plans.append({
                        "id": opt_id, "method": p_method, "plan": plan_str, "total": total,
                        "first": first_dt, "num": num_p, "req_sp": needs_sp, "chg": chg,
                        "exp": f"Use {num_p} installments of {home_curr} {p_amt:,.2f}, starting {first_dt.strftime('%d %B %Y').lstrip('0')}."
                    })

            if eligible_plans:
                eligible_plans.sort(key=lambda x: (x["total"], x["req_sp"], x["first"], x["num"], x["id"]))
                best = eligible_plans[0]
                status = "affordable_with_plan"
                method = best["method"]
                plan = best["plan"]
                changes = best["chg"]
                exp = best["exp"]

            elif earliest_full_date and "full_payment" in considered:
                e_dt = datetime.strptime(earliest_full_date, "%Y-%m-%d")
                if e_dt <= target_dt and e_dt <= (req_dt + timedelta(days=90)):
                    status = "affordable_later"
                    method = "wait"
                    plan = f"{earliest_full_date}:{int(req_amount) if req_amount.is_integer() else req_amount:.2f}".rstrip('0').rstrip('.')
                    exp = f"Pay {home_curr} {req_amount:,.2f} in full on {e_dt.strftime('%d %B %Y').lstrip('0')}."
                else:
                    status = "not_affordable"
                    method = "not_recommended"
                    plan = "none"
                    earliest_full_date = ""
                    exp = f"Do not proceed with the {home_curr} {req_amount:,.2f} request."

            else:
                status = "not_affordable"
                method = "not_recommended"
                plan = "none"
                earliest_full_date = ""
                exp = f"Do not proceed with the {home_curr} {req_amount:,.2f} request."

        return {
            "request_id": req_id,
            "amount_safe_to_pay": round(amount_safe_to_pay, 2),
            "affordability_status": status,
            "recommended_payment_method": method,
            "payment_plan": plan,
            "earliest_date_for_full_payment": earliest_full_date,
            "spending_changes_needed": changes,
            "decision_explanation": exp
        }