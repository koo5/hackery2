
def split_list_on_last_occurence_of_separator(list,separator):
    for i_idx,i in enumerate(list):
        if i == separator:
            sep_idx = i_idx
    assert(sep_idx)

    before,after=[],[]

    for i_idx,i in enumerate(list):
        if i_idx < sep_idx:
            before.append(i)
        elif i_idx > sep_idx:
            after.append(i)

    return before,after


print(split_list_on_last_occurence_of_separator([1,2,'--',2,'--',3],'--'))
