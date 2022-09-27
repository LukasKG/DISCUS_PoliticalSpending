import pandas as pd
import numpy as np

def get_nth_key(dictionary, n=0):
    if n < 0:
        n += len(dictionary)
    for i, key in enumerate(dictionary.keys()):
        if i == n:
            return key
    raise IndexError("dictionary index out of range") 

def get_totals(invoice_amounts,total_values,prediction):
    totals = np.zeros_like(total_values)
    for amount, cat in zip(invoice_amounts,prediction):
        totals[cat] += amount
    return totals

def get_error(invoice_amounts,total_values,prediction,loss='MSE',return_totals=False,return_diff=False):
    diff = total_values - get_totals(invoice_amounts,total_values,prediction)
    if loss == 'MSE':
        error = np.square(diff)
    else:
        error = np.abs(diff)
        
    r = [np.mean(error)]
    if return_totals: r+= [totals]
    if return_diff: r+= [diff]
    return r

def random_solver(invoice_amounts,total_values,loss='MSE',max_iter=5,max_waiting_iter=1):
    factor = invoice_amounts.shape[0] ** (len(total_values)-1)
    max_iter = int(max_iter * factor)
    max_waiting_iter = int(max_waiting_iter * factor)
    pred = np.random.randint(low=0, high=len(total_values), size=invoice_amounts.shape[0], dtype=int)

    error, diff = get_error(invoice_amounts,total_values,pred,loss,return_diff=True)
    wait = 0
    unvisited = list(range(len(pred)))
    while len(unvisited) > 0:   
        idx = unvisited.pop(0)
        cat = pred[idx]
        
        #print(idx,unvisited)
        
        error_, diff_, cat_ = error, diff, cat
        for c in range(len(total_values)):
            if c==cat: continue
            pred[idx] = c
            e, d = get_error(invoice_amounts,total_values,pred,loss,return_diff=True)
            #print(f"{c=} {e=}")
            if e<error_:
                error_, diff_, cat_ = e, d, c
                
        if error_ < error:
            unvisited = list(range(len(pred)))
            np.random.shuffle(unvisited)
            #print(f"Improvement! {error_}")

                
        pred[idx] = cat_
        error, diff = error_, diff_
            
    return pred

def genetic_algorithm(invoice_amounts,total_values,loss='MSE',N=100,max_iter=50,mutationRate=None,min_error=0.01):
    def calcFit(prediction):
        return get_error(invoice_amounts,total_values,prediction,loss=loss)[0]
    
    No_Gen = invoice_amounts.shape[0]
    No_Typ = len(total_values)
    
    if mutationRate is None:
        mutationRate = 1/No_Gen
    
    #factor = No_Gen ** (No_Typ-1)
    factor = 1
    total_iter = int(max_iter * factor * N)
    
    indeces = np.array(range(N))
    pop = np.random.randint(low=0, high=No_Typ, size=(N,No_Gen), dtype=int)
    fit = np.array([calcFit(pred) for pred in pop])
    
    minFit_idx = np.argmin(fit)
    minFit = fit[minFit_idx]
    #print(f"Minimum: {minFit:.2f} (Idx = {minFit_idx}); solution: {pop[minFit_idx]}")
    
    if minFit > min_error:
        for it in range(total_iter*N):
            champs = np.random.choice(indeces, size=2, replace=False)

            # determine winner
            if fit[champs[1]] < fit[champs[0]]:
                champs[0],champs[1] = champs[1],champs[0]

            # uniform crossover
            for j in range(No_Gen):
                # Mutation chance
                if np.random.random() < mutationRate:
                    pop[champs[1],j] = np.random.randint(low=0, high=No_Typ, size=1, dtype=int)

                # 50% chance of overwritting
                elif np.random.random() < 0.5:
                    pop[champs[1],j] = pop[champs[0],j]


            # determine fitness of newly combined individual
            fit[champs[1]] = calcFit(pop[champs[1]])

            if fit[champs[1]] < minFit:
                minFit, minFit_idx = fit[champs[1]], champs[1]
                #print(f"It {it} Minimum: {minFit:.2f} (Idx = {minFit_idx}); solution: {pop[minFit_idx]}")
          
                if minFit < min_error:
                    break
                    
            # Print every N iterations
            if (it+1)%N == 0:
                print(f"{(it+1)//N}/{total_iter}: Fitness: {minFit:.2f} Solution: {pop[minFit_idx]}")
    return pop[minFit_idx]

def run(solver='GA',N=100,verbose=False):
    data_coding = pd.read_csv('data/processed/coding_both.csv')
    data_invoice = pd.read_csv('data/processed/invoices.csv')

    ## TODO add CSV with manual set invoice amounts
    #data_preset = pd.read_csv('data/input/invoices_manual.csv')
    
    parties = pd.concat((data_coding['Party'], data_invoice['RegulatedEntityName'])).unique()
    categories = data_coding.columns[5:]

    error_acc = 0
    row_list = []

    for party in parties:
        party_coding = data_coding[ data_coding['Party']==party ]
        party_invoice = data_invoice[ data_invoice['RegulatedEntityName']==party ]

        suppliers = pd.concat(( party_coding['Supplier'], party_invoice['SupplierName'] )).unique()

        for supplier in suppliers:
            sup_coding = party_coding[ party_coding['Supplier']==supplier ]
            sup_invoice = party_invoice[ party_invoice['SupplierName']==supplier ]

            sup_cats = {}

            for cat in categories:
                val = np.sum(sup_coding[cat].values)
                if val >= 0.01:
                    sup_cats[cat] = val

            if len(sup_cats) < 1:
                continue
            
            if verbose:
                spent = np.round(sup_coding['Total Spend'].sum(),2)
                filed = np.round(sup_invoice['TotalExpenditure'].sum(),2)


                print(f"{party} - {supplier}")
                print(f"Diff = {abs(spent-filed)} ({spent=} | {filed=}) accross {len(sup_cats)} categories with {sup_coding.shape[0]} codings and {sup_invoice.shape[0]} invoices.")

            # Estimate a proper matching if there's more than one invoice
            # random encoding which invoice belongs to which category
            if sup_invoice.shape[0] > 1:
                values = np.fromiter(sup_cats.values(), dtype=float)
                invoices = sup_invoice['TotalExpenditure'].values

                if len(values) <= 1:
                    prediction = np.zeros(invoices.shape[0],dtype=int)
                else:
                    if solver == 'GA':
                        prediction = genetic_algorithm(invoices,values,loss='MSE',N=N,max_iter=len(values)**3,mutationRate=0.02)
                    else:
                        # Absolute error is fine for random solver as only one position is changed at the time
                        prediction = random_solver(invoices,values,loss='MAE')

                # get non-squared error
                error = get_error(invoices,values,prediction,loss='MAE')[0]
                error_acc += error

                for i, (idx, row) in enumerate(sup_invoice.iterrows()):
                    val = row['TotalExpenditure']
                    entry = {
                        'ECRef': row['ECRef'],
                        'InvoiceID': row['RedactedSupportingInvoiceId'],
                        'Supplier': supplier,
                        'Party': party,
                        'Total Spend': val,
                        'Error': error,
                        'Expense Category (Coding)': sup_coding['Expense Category'].mode()[0],
                        'Expense Category (Invoice)': row['ExpenseCategoryName'],
                        **{k:0 for k in categories}
                            }

                    cat = get_nth_key(sup_cats, n=prediction[i])
                    entry[cat]=val

                    row_list.append(entry)
            else:
                row = sup_invoice.iloc[0]
                entry = {
                    'ECRef': row['ECRef'],
                    'InvoiceID': row['RedactedSupportingInvoiceId'],
                    'Supplier': supplier,
                    'Party': party,
                    'Total Spend': row['TotalExpenditure'],
                    'Error': 0.0,
                    'Expense Category (Coding)': sup_coding['Expense Category'].mode()[0],
                    'Expense Category (Invoice)': row['ExpenseCategoryName'],
                    **{k:0 for k in categories}
                        }
                entry.update(sup_cats)
                row_list.append(entry)

    df = pd.DataFrame.from_dict(row_list)
    df.to_csv('data/processed/invoices_matched.csv', index=False)
    if verbose:
        print("Error:",error_acc)
        
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--solver", type=str, help="Options: \'GA\' for genetic algorithm; \'random\' for random solver", default='GA', dest='solver')
    parser.add_argument("-N","--popsize", type=int, help="Number of individuals in the genetic algorithm", default=100, dest='N')
    parser.add_argument("-v","--verbose", help="increase output verbosity", dest='verbose', action="store_true")
    args = parser.parse_args()
    
    run(solver=args.solver,N=args.N,verbose=args.verbose)