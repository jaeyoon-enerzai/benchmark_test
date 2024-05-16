def create_table_header(commit, comm_same_group, comm_all_group):
    content = '|'
    strnum_list = []
    
    header = 'Model Name'
    num = 30
    strnum_list.append(num)
    content += f'{header:^{num}}<br>|'
    
    header = f'current run'
    num = 25
    strnum_list.append(num)
    commit = f'({commit[:8]})'
    content += f'{header:^{num}}<br>{commit}|'
    
    header = f'current commit'
    num = 25
    strnum_list.append(num)
    commit = f'{commit[:8]})'
    content += f'{header:^{num}}<br>{commit}|'
    
    header = f'Best under same group'
    num = 25
    strnum_list.append(num)
    commit = f'({comm_same_group[:8]})'
    content += f'{header:^{num}}<br>{commit}|'
    
    header = f'Best under all groups'
    num = 25
    strnum_list.append(num)
    commit = f'({comm_all_group[:8]})'
    content += f'{header:^{num}}<br>{commit}|'
    
    content += '\n|'
    for n in strnum_list:
        content += ':'
        content += '-' * n
        content += ':|'
    return content, strnum_list