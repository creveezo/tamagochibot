from helpedit_funcs import get_smth

def if_alive(id):
    try:
        get_smth('id', id)
        return 1
    except Exception:
        return 0
    
def if_plot_now(id):
    n = get_smth('action_number', id)
    stage = get_smth('stage', id)
    if stage == 0:
        if n == 12: 
            ans = 0
        else:
            ans = 1
    return ans