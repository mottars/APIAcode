#import xlrd
import numpy as np

def read_txt_file(filename, transp=False): 
    arquivo = open(filename)
    mtrx = arquivo.read()
    arquivo.close()

    mtrx = mtrx.split('\n')
    matrix = []
    for i in range(len(mtrx)):
        # print(mtrx)
        matrix.append(mtrx[i].split('\t'))

    # print(matrix)
    matrix[0][0] = '0'
    
    matrix = np.array(matrix, float)

    if (transp == True):
        matrix = np.transpose(matrix)

    return matrix

def read_excel_file(filename, transp=False):
    workbook = xlrd.open_workbook(filename)

    """ Planilha com a matriz do perfil de defeito """
    worksheet = workbook.sheet_by_index(1)

    # Change this depending on how many header rows are present
    # Set to 0 if you want to include the header data.
    offset = 0

    rows = []
    for i, row in enumerate(range(worksheet.nrows)):
        #if i <= offset:  # (Optionally) skip headers
        #    continue
        r = []
        for j, col in enumerate(range(worksheet.ncols)):
            r.append(worksheet.cell_value(i, j))
        rows.append(r)

    rows[0][0] = rows[0][1] = 0

    # Remove linha e coluna em branco
    rows = np.delete(rows, (1), axis=0)
    rows = np.delete(rows, (1), axis=1)

    matrix = np.array(rows, float)

    if (transp == True):
        matrix = np.transpose(matrix)

    """ Planilha com as propriedades do perfil de defeito """
    """
    worksheet = workbook.sheet_by_index(0)

    l = worksheet.cell_value(1,1)
    rE = worksheet.cell_value(2,1)/2
    t = worksheet.cell_value(3,1)
    """
    return matrix

# read_txt_file('TS02.txt')