import numpy as np
import os
import pandas as pd
   
in_path = 'data/raw'
out_path = 'data/processed'
    
df_t = pd.read_csv(os.path.join(in_path,'coding_transport.csv'), dtype="object", header = 1)
df_n = pd.read_csv(os.path.join(in_path,'coding_notransport.csv'), dtype="object", header = 1)

frames = []
for df in (df_t, df_n):
    # Remove empty columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Remove whitespaces
    df.columns = df.columns.str.strip()

    # Drop unneccesary columns
    df.drop(['Notes','More than 1 service','Supplier .1','Supplier.1','Missing invoices?'], axis=1, errors='ignore', inplace=True)
    
    # Rename for uniform names and clarity
    df.rename(columns = {
        'ADVERTISING AND PRESS': 'Advertising and Press',
        'Ambiguous and needs discussion': 'Ambiguous',
        'Campaign database or CRM (including SQL)': 'Campaign database or CRM',
        'Creative content owned by a third party (e.g. Getty images, PA images, demo music)': 'Creative content',
        'Event costs/ Production/ Venue hire': 'Event costs/Venue hire',
        'Office infrastructure and supplies': 'Office supplies',
        'Office supplies (staples, paperclips, IT equipment, envelopes)' : 'Office supplies',
        'Online advertising (i.e. web advertising but not online newspapers or social media)': 'Online advertising',
        'Online advertising (not social media,  i.e. web advertising but not online newspapers or social media)': 'Online advertising',
        'Other forms of advertising (billboards, advans, digital posters outside)': 'Other forms of advertising',
        'Direct Mail/ Leaflet delivery/ postage': 'Postage',
        'Paid leaflet delivery/ postage': 'Postage',
        'Video editing/ production': 'Video editing/production',
        
    }, inplace = True)
    
    frames.append(df)

print("\nUnique columns left:")
t,n = list(frames[0].columns),list(frames[1].columns)
for col in sorted(set(t+n)):
    if col in t and col in n:
        continue
    elif col in t:
        print("    Transport:",col)
    else:
        print("Non-Transport:",col)


df = pd.concat(frames, axis=0)

# Fill NaNs with '0'
df.fillna('0', inplace=True)

# Add ID column
df.insert(0, 'ID', [str(n) for n in range(len(df))])

'''
0 - ID
1 - Supplier
2 - Party
3 - Total Spend
4 - Expense Category
'''

# Convert string into float values
for col in ['Total Spend']+list(df.columns[5:]):
    df[col] = df[col].str.replace('£', '')
    df[col] = df[col].str.replace(',', '')
    df[col] = df[col].astype(float)


print("\nAll",len(df.columns),"column names:")
for col, col_type in zip(df.columns,df.dtypes):
    print("   NaNs" if df[col].isnull().values.any() else "No NaNs",col_type,col)

df_coding = df
df = None    



'''

 Invoice list

'''

# Open invoice list
df_invoice = pd.read_csv(os.path.join(in_path,'invoice_list.csv'))

# Drop entries w/o provided invoices
df_invoice = df_invoice[df_invoice['RedactedSupportingInvoiceId'].notna()]

# Convert invoice ID to str
df_invoice['RedactedSupportingInvoiceId'] = df_invoice['RedactedSupportingInvoiceId'].astype(int).astype(str)

# Convert total spend to float
df_invoice['TotalExpenditure'] = df_invoice['TotalExpenditure'].str.replace('£', '')
df_invoice['TotalExpenditure'] = df_invoice['TotalExpenditure'].str.replace(',', '')
df_invoice['TotalExpenditure'] = df_invoice['TotalExpenditure'].astype(float)
    
print("\nInvoice column names:")
for col, col_type in zip(df_invoice.columns,df_invoice.dtypes):
    print("   NaNs" if df_invoice[col].isnull().values.any() else "No NaNs",col_type,col)

    
    
def print_sets(name,lst_coding,lst_invoice):
    print("\n"+name+" Coding:")
    for item in lst_coding:print(item)

    print("\n"+name+" Invoices:")
    for item in lst_invoice:print(item)

    print("\nUnique "+name+" left:")
    for item in sorted(set(lst_invoice+lst_coding)):
        if item in lst_invoice and item in lst_coding:
            continue
        print(" Coding:" if item in lst_coding else "Invoice:",item)

def replace_items(df,col_name,d):
    for k,v in d.items():
        df[col_name].replace(k,v,inplace=True)
        
'''
    ###################
       Handle Parties
    ###################
'''
d_party = {
    'Christian Party "Proclaiming Christ\'s Lordship"': 'Christian Party',
    'Co-operative Party': 'Co-op Party',
    'Conservative and Unionist Party': 'Conservative Party',
    'Conservatives ': 'Conservative Party',
    'Greens': 'Green Party',
    'Labour': 'Labour Party',
    'Plaid Cymru - The Party of Wales': 'Plaid Cymru',
    'Scottish National Party (SNP)': 'Scottish National Party',
    'Scottish Green Party': 'Green Party',
    'The Women\'sEquality Party': 'Womens Equality Party',
    'UK Independence Party (UKIP)': 'UKIP',
    'Women\'s Equality Party': 'Womens Equality Party',
}
replace_items(df_coding,col_name='Party',d=d_party)   
coding_parties = sorted(df_coding['Party'].unique())

replace_items(df_invoice,col_name='RegulatedEntityName',d=d_party)
invoice_parties = sorted(df_invoice['RegulatedEntityName'].unique())

print_sets(name='Parties',lst_coding=coding_parties,lst_invoice=invoice_parties)
    
        
'''
    ###################
       Handle Suppliers
    ###################
'''

# Remove Whitespaces
df_coding['Supplier'] = df_coding['Supplier'].str.strip()
df_invoice['SupplierName'] = df_invoice['SupplierName'].str.strip()

d_supplier = {
    'Tindle Newspapers Devon Limited': 'Tindle Newspapers',
    'Tindle Newspapers Limited': 'Tindle Newspapers',
    'Tindle Newspapers Wales & The Borders Ltd': 'Tindle Newspapers',
    'Tindle Newspapers West Country Limited': 'Tindle Newspapers',
    
    'Twitter International Company': 'Twitter',
    'Twitter International Limited': 'Twitter',
    'Twitter Uk Ltd': 'Twitter',

    
    'Whistl (Doordrop Media) Ltd' : 'Whistl',
    'Whistl UK' : 'Whistl',
    'Whistl UK Limited' : 'Whistl',
    
    'YouGov UK': 'YouGov',
    'YouGov plc': 'YouGov',
    'YouGovUK': 'YouGov',

}

replace_items(df_coding,col_name='Supplier',d=d_supplier)  
coding_suppliers = sorted(df_coding['Supplier'].unique())

replace_items(df_invoice,col_name='SupplierName',d=d_supplier) 
invoice_suppliers = sorted(df_invoice['SupplierName'].unique())

print_sets(name='Supplier',lst_coding=coding_suppliers,lst_invoice=invoice_suppliers)



# Save processed csv
df_coding.to_csv(os.path.join(out_path,'coding_both.csv'),index=False)  
df_invoice.to_csv(os.path.join(out_path,'invoices.csv'),index=False) 
