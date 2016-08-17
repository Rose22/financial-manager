import sys
import imp
from custom_shell import BaseShell, GenericShell

imp.load_source("config", "finance.conf")
import config

class PaymentsShell(BaseShell):
    def __init__(self, payments_list):
        self.payment_type  = payments_list.name
        self.payments_list = payments_list

    def display_list(self):
        print self.payments_list

    def run_loop(self):
        print "Managing %s" % self.payment_type
        print

        disable_display = False
        while True:
            if not disable_display:
                print self.payments_list

                print "---"

            cmd = self.input_type("string", "Do what? (add, edit, move, delete, clear, back)>")
            if cmd:
                cmd = cmd.lower()

            disable_display = False

            if cmd in ["add", "a"]:
                self.prompt_add_payment()
            elif cmd in ["edit", "e"]:
                index = self.input_type("int", "Edit which one?>")

                if index is False:
                    return False

                print

                self.prompt_edit_payment(index)
            elif cmd in ["move", "m"]:
                index = self.input_type("int", "Move which one?>")

                if index is False:
                    return False

                print

                self.prompt_move_payment(index)
            elif cmd in ["delete", "d"]:
                index = self.input_type("int", "Delete which one?>")

                if index is False:
                    return False

                print

                self.prompt_delete_payment(index)
            elif cmd in ["search", "s"]:
                self.prompt_search()
                disable_display = True

            elif cmd in ["clear"]:
                confirm = self.input_type("string", "Are you sure you want to clear the list? (y/N)>")
                if confirm in ['y', 'yes']:
                    self.payments_list.payments = []
                    print "List cleared."

            elif cmd in ['back', 'b', 'exit', 'quit', 'q']:
                return True

            print "---"
            print

    def prompt_add_payment(self):
        category  = self.input_type("string", "What kind of item is it?>")
        name      = self.input_type("string", "What's the name of it?>")
        price     = self.input_type("float", "How much price did/will you spend?>")
        day       = self.input_type("day", "On what day did/does the %s get billed?" % self.payment_type)

        if not category:
            category = "Generic"
        if not name:
            return False
        if not price:
            return False
        if not day:
            return False

        self.payments_list.add(price, category, name, day)
        return True

    def prompt_edit_payment(self, index):
        if not self.payments_list.exists(index):
            print "That item did not exist!"
            return False

        unedited_payment = self.payments_list.get()[index]

        category  = self.input_type("string", "What's kind of item is it? (leave empty to leave unchanged)>")
        name      = self.input_type("string", "What's the name of it? (leave empty to leave unchanged)>")
        price     = self.input_type("float", "How much money did/will you spend? (leave empty to leave unchanged)>")
        day       = self.input_type("day", "On what day did/does the %s get billed? (leave empty to leave unchanged)>" % (self.payment_type))

        if not category:
            category = unedited_payment['category']
        if not name:
            name = unedited_payment['name']
        if not price:
            price = unedited_payment['price']
        if not day:
            day = unedited_payment['day']

        if self.payments_list.edit(index, price, category, name, day):
            print "Edited"

    def prompt_move_payment(self, index):
        new_index = self.input_type("int", "Move it to which position? (leave empty to leave unchanged)>")

        if not index:
            return False

        self.payments_list.get().insert(new_index, self.payments_list.get().pop(index))
        print "Moved."

    def prompt_delete_payment(self, index):
        if not self.payments_list.exists(index):
            print "That item did not exist!"
            return False

        confirm = self.input_type("string", "Delete [%s]? (y/N)>" % self.payments_list.get()[index]['name'])
        if confirm.lower() in ['y', 'yes']:
            if self.payments_list.delete(index):
                print "Deleted."

    def prompt_search(self):
        key    = self.input_type("search", "Search within what? (day, category, name, price)>")
        query  = self.input_type("string", "For what?>")

        if not key:
            return
        if not query:
            return

        print

        print self.payments_list.display(key, query)

class MainShell(GenericShell):
    main_shell = True
    prompt = "Manager>"
    intro = """Financial Manager by Rose
Type 'help' for help.

Quick reminder: income, expenses, payments, +payments, total, budget, details, foresight, nextmonth, setleftovers, exit
"""
    currency = "$"

    def __init__(self, data_manager):
        self.data_manager       = data_manager
        self.shells             = {
            "payments":         PaymentsShell(self.data_manager.get_payments("payments")),
            "+payments":        PaymentsShell(self.data_manager.get_payments("+payments")),
            "expenses":         PaymentsShell(self.data_manager.get_payments("expenses")),
            "income":           PaymentsShell(self.data_manager.get_payments("income"))
        }

        self.cmd_associations = {
            'setleftovers':         self.cmd_set_leftovers,
            'sl':                   self.cmd_set_leftovers,

            'payments':             self.cmd_manage_payments,
            'p':                    self.cmd_manage_expenses,

            '+payments':            self.cmd_manage_plus_payments,
            '+p':                   self.cmd_manage_plus_payments,

            'expenses':             self.cmd_manage_expenses,
            'e':                    self.cmd_manage_expenses,

            'income':               self.cmd_manage_income,
            'i':                    self.cmd_manage_income,

            'total':                self.cmd_display_total,
            'budget':               self.cmd_display_budget,
            'shortbudget':          self.cmd_display_short_budget,
            'details':              self.cmd_display_details,
            'foresight':            self.cmd_display_foresight,

            'nextmonth':            self.cmd_next_month,

            'help':                 self.help,

            'exit':                 self.cmd_exit,
            'quit':                 self.cmd_exit,
            'q':                    self.cmd_exit
        }

    def help(self):
        print """
Simply set your income, then add your monthly expenses/bills. You can do this every month, or only once if your expenses are the same every month.

The program then calculates a budget. This is the money you have left over after all the bills are paid..
The budget represents the amount of money you REALLY have - I.E. that you can spend on fun stuff and on groceries.

Add a payment every time you buy something to keep track of how much money you still have left :)

The program tracks how much money you have left at the end of each month. When you move onto the next month,
the program will add the money you had left in the previous month, to the budget in your current month.
This additional budget is called "leftovers" within the manager.
That way, if you save well, your budget will grow :)

---

income:                 Manage your monthly income
expenses:               Manage your monthly expenses/bills
payments:               Manage your payments
+payments:              Manage the money you gained this month

total:                  Shows your income and budget
shortbudget:            Shows your current budget, short version
budget:                 Shows your current budget and money left
details:                Shows income, budget, money left, and an overview of all expenses and payments

foresight:              Shows how much money you would have next month, if you were to not buy anything anymore this month.
setleftovers:           Set your leftovers to a manual value in case you need to correct it
nextmonth:              Moves the manager onto the next month, which means it stores your leftover money from this month, which gets added to your budget.

exit:                   Quits the program
        """,

    def cmd_get_income(self):
        print self.data_manager.get_income()
    def cmd_set_income(self):
        current_income = self.input_type('float', "What's your current income?>")
        if current_income:
            self.data_manager.set_income(current_income)
            print "Income set"

    def cmd_get_leftovers(self):
        print self.data_manager.get_leftovers()
    def cmd_set_leftovers(self):
        leftovers = self.input_type('float', "How much money did you have left over?>")
        if leftovers:
            self.data_manager.set_leftovers(leftovers)
            print "Leftovers set"

    def cmd_manage_expenses(self):
        self.shells['expenses'].run_loop()
        self.data_manager.save()

    def cmd_manage_income(self):
        self.shells['income'].run_loop()
        self.data_manager.save()

    def cmd_manage_payments(self):
        self.shells['payments'].run_loop()
        self.data_manager.save()

    def cmd_manage_plus_payments(self):
        self.shells['+payments'].run_loop()
        self.data_manager.save()

    def cmd_display_total(self):
        print "Income: %s%.2f" % (config.currency, self.data_manager.get_payments_total("income"))
        print "Monthly Expenses: %s%.2f" % (config.currency, self.data_manager.get_payments_total('expenses'))
        print
        print "Monthly allowed budget, based on income minus expenses: %s%.2f" % (config.currency, self.data_manager.get_pure_budget())
        print
        print "Leftovers from previous month: %s%.2f" % (config.currency, self.data_manager.get_leftovers())
        print "Extra money gained (+payments): %s%.2f" % (config.currency, self.data_manager.get_payments_total("+payments"))
        print
        print "Resulting Budget: %s%.2f" % (config.currency, self.data_manager.get_budget())
        print "Payments so far: %s%.2f" % (config.currency, self.data_manager.get_payments_total("payments"))
        print "Money left: %s%.2f" % (config.currency, self.data_manager.get_money_left())

    def cmd_display_budget(self):
        print "budget: %s%.2f (prev month: %s%.2f), payments: %s%.2f, money left: %s%.2f" % (config.currency, self.data_manager.get_budget(), config.currency, self.data_manager.get_leftovers(), config.currency, self.data_manager.get_payments_total("payments"), config.currency, self.data_manager.get_money_left())

    def cmd_display_short_budget(self):
        print "{0}{1:>05.2f} of {2}{3:>05.2f}".format(config.currency, self.data_manager.get_money_left(), config.currency, self.data_manager.get_budget())

    def cmd_display_details(self):
        print "---"
        print

        print "Income:"
        print self.data_manager.get_payments("income")
        print "---"
        print "Monthly Expenses:"
        print self.data_manager.get_payments("expenses")
        print "---"
        print "Payments:"
        print self.data_manager.get_payments("payments")

        print "---"
        print "Money left: %s%.2f" % (config.currency, self.data_manager.get_money_left())
        print "---"

    def cmd_display_foresight(self):
        print "Based on your current available money, the predicted amount of money next month is {0}{1:05.2f}".format(config.currency, self.data_manager.get_foresight())

    def cmd_next_month(self):
        print "WARNING: This will clear your entire list of payments and move the money you currently have available, into your leftovers. Your expenses will stay intact."
        print

        confirm = self.input_type("string", "Would you really like to move on to the next month?>")
        if confirm.lower() in ['yes', 'y']:
            self.data_manager.next_month()
            print "Moved on to the next month."

    def cmd_exit(self):
        sys.exit(0)