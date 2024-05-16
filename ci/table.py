def create_table_header(commit, comm_same_group, comm_all_group):
    content = '|'
    strnum_list = []
    
    header = 'Model Name'
    num = 30
    strnum_list.append(num)
    content += f'{header:^{num}}|'
    
    header = f'current commit'
    num = 25
    strnum_list.append(num)
    strnum_list.append(num)
    content += f'{header:^{num}}|'
    
    header = f'Best under same group'
    num = 25
    strnum_list.append(num)
    content += f'{header:^{num}}|'
    
    header = f'Best under all groups'
    num = 25
    strnum_list.append(num)
    content += f'{header:^{num}}|'
    
    content += '\n|'
    commits = ['', f'({commit[:20]})', f'({comm_same_group[:20]})', f'({comm_all_group[:20]})']
    
    for c, n in zip(commits, strnum_list):
        content += f'{c:^{n}}|'
    
    content += '\n|'
    for n in strnum_list:
        content += '-' * n
        content += '|'
    return content, strnum_list