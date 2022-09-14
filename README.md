# Breakdown of campaign spendings during the general election 2019

## Match Suppliers

### Challenge

The initial challenge arrises from the fact that there's no direct link between the invoices provided by the electoral college and the categories assigned to the expenses by Dr. Power and his team. The **invoice list** obtained from the electoral college, lists every invoice with an unique ID, the party, the supplier, a rough estimation of the expense category, the expense, and an ID if there is an attachement provided (e.g. scan of the physical invoice). The **coding list** provided by Dr. Power lists for every existing combination of party and suppliers a detailed breakdown which amounts were spent on each of the 58 listed categories. However, this can be an accumulation of multiple invoices between the party and a particular supplier and hence, this bridge must be gaped in order to obtain a supervised training set, where each invoice can be linked to one or multiple spending categories.

### Match the amounts

Before solving the task of matching individual invoice positions, we first aimed to match the total amounts. By summing up all expenses between each unique party - supplier combination in both the invoice and the coding list, only 50% of the amounts could be matched. Misspellings, white spaces, and different spellings of both, parties and suppliers, were identified as issue (e.g. GOOGLE UK and Google). This problem is tackled in [connect_csv](connect_csv.py) by removing whitespaces and keywords like "Ltd" from names. There is also a long list of converting names to unifying pendants which was developed during multiple iterations of identifying similar names or similar unlinked amounts as identified in the snippet below.

<p align="center">
  <img src="https://github.com/LukasKG/DISCUS_PoliticalSpending/blob/main/img/last_matching.png" />
</p>

After all adjustments, £49,540,640.20 (98.9%) could be matched, whereas £20,115.23 (0.0%) of the amounts listed in the coding list could not be linked to the invoices and £516,562.91 (1.0%) of the amounts in the invoices could not be linked to the coding list.

## Download invoices

The script to [download the invoice files](download_invoices.py) takes the [invoice list](/data/raw/invoice_list.csv) obtained from the electoral college, identifies every entry with a provided supporting invoice, and uses these IDs to download the provided files. In total, 22,720 positions are listed by the electoral college, out of which 6,396 have an invoice attached.
 
# Original Brief for DISCUS Hackathon:

## Money in politics: how do political parties spend their campaign war chests?
 
*Dr Sam Power, Lecturer in Corruption Analysis in the Politics Department, University of Sussex*

### Outcome: 
On what services is money spent at elections? This is primary question behind this project. We know that just over £50 million was spent at the last general election, but strikingly little about how. Parties have to report their spending to the Electoral Commission under broad categories (e.g. ‘advertising’ and ‘market research and canvassing’), but this provides very little detail. They do, however, have to provide invoices for any spend over £200 so there is a vast resource available to find out more.
 
### Challenge: 
To address this gap, I (with a research team) manually coded every invoice (6,396) that was submitted to the Electoral Commission by political parties at the 2019 general election – which allowed us to paint a better picture of overall spend. These findings were written up into a report, a blog, and covered in the national media. The challenge here might seem obvious. It took ages and was incredibly arduous. There is much more information, available from many other elections, that could be analysed. I think, quite simply, there must be a better way. And perhaps that is via machine learning.
 
### Data: 
What we have to facilitate this better way, is a fantastic training set. I have provided two excel spreadsheets which contain the spending from the coding exercise. They have the name of the party conducting the spend, the amount of spend and the category that said spend falls under (you can see the amount of money written in the category). The Electoral Commission ‘political finance database’ hosts all of the invoices. 
 
### Relevant context: 
The suppliers that political parties use at elections took on new prominence after the Cambridge Analytica Scandal. And concerns about the ways in which modern technology, particularly social media platforms, are changing elections – and more widely democracy itself – are front and centre in the minds of many of us that study politics. But without a clear understanding on just what money is spent on, we cannot make a reasonable judgement about whether these trends are damaging and, if they are, how to combat them. 
