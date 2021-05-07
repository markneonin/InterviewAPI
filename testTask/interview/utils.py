from datetime import datetime


def is_valid_selection_answer(answer, question):
    if answer['question'] == question[0].id:
        quantity = len(answer['choices'])
        if quantity != 1 and question[0].lock_other:
            return
        elif not quantity:
            return
        else:
            for choice in answer['choices']:
                if (choice,) not in question[1]:
                    return
        return True
    else:
        return


def now():
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f+03:00")
    return time_str
