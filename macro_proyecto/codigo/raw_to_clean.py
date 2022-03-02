#librerias a usar
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame



#funciones a usar
def cleanse_rows(row: str) -> str:
  '''Funcion para eliminar los caracteres \r\n > hallados en los datos.
  
  Parametros
  --------------
  row: str
    fila con caracteres \r\n > \n del dataframe

  Returns
  ------------
  str
    fila sin caracteres \r\n > \n
  '''
  
  cleansed_row = row.replace("\r\n", "").replace(">", "").replace("\n", "")
  return cleansed_row


def apply_in_rows(df:pd.core.frame.DataFrame, function_to_apply, drop_columns: list = [],):
  '''Funcion para aplicar a cada una de las columnas de un dataframe una funcion determinada
  
  Parametros
  -------------
  data_frame:
    DataFrame al cual se le quiere aplicar la funcion por columnas
  function_to_apply: function
    Funcion que se le quiere aplicar a determinadas columnas del DataFrame
  drop_columns:
    Columnas del DataFrame a las cuales no se le quiera aplicar la funcion
  
  Returns
  -------------
  pd.core.frame.DataFrame
    Devuelve un DataFrame con la funcion aplicada en las columnas deseadas
  '''

  columns = df.columns
  if len(drop_columns) > 0:
    for column in drop_columns:
      columns.drop(column) #quito las columnas a las que no les voy a aplicar la funcion

  for column in columns:
    df[column] = df[column].apply(function_to_apply)
  return df


def hex_to_value(row:str, column: str)->int or str:
  '''Funcion para convertir las cadenas hexadecimales que contiene el dataframe en valores numericos

  Parametros
  --------------
  row: str
    Fila del dataframe que contiene la cadena hexadecimal
  column: str
    Tipo de la columna de la cual estoy conviertiendo los datos; la formula para convertir hexadecimal
    a numerico cambia dependiendo del tipo de columna

  Returns
  -------------
  int
    Valor numerico obtenido de la conversion de hexadecimal - numerico
  str
    Si la columna ingresada no es [RPM, TEMP, VEL, LOAD] la columna no se encuentra definida
  '''
  
  if len(row) > 0:
    row_wo_spaces = row.replace(" ", "") #le quito los espacios a la fila
    str_split = len(row_wo_spaces) - 2 #cojo la longitud de la cadena y le resto 2 para poder obtener los ultimos 2 caracteres
    hex_number = row_wo_spaces[str_split:] #BYTE A
    int_number = int(hex_number, 16) #convierto el hexa a entero
    if column == "RPM":
      #en este caso en particular el hex_number pasa a ser el BYTE B
      byte_a = row_wo_spaces[str_split-2:str_split]
      int_byte_a = int(byte_a, 16)
      value = ((int_byte_a*256)+int_number)//4
    elif column == "TEMP":
      value = int_number-40
    elif column == "VEL":
      value = int_number
    elif column == "LOAD":
      value = round((int_number*100)/255,2) #redondeo a 2 decimales
    else:
      return "Columna no definida!"
    return value

  return row #si la longitud es 0 retorno fila


def drop_missing_values(values: list) -> list:
  '''Funcion que crea una lista sin valores faltantes ("")
  
  Parametros
  ------------
  values:list
    Lista de valores que posee valores faltantes ("")

  Returns
  -----------
  list
    Lista sin valores faltantes ("")
  '''

  wo_missing = [value for value in values if value != ""] #si el valor no es igual a "" se guarda en la lista
  return wo_missing


def get_df_mean_std(df: pd.core.frame.DataFrame, drop_columns:list = []) -> dict:
  '''Funcion para crear un diccionario con los datos: media, deviacion estandar, limite superior de la desviacion estandar, 
  limite_inferior de la desviacion estandar por cada una de las columnas de un dataframe
  
  Parametros
  ------------
  df: pd.core.frame.DataFrame
    DataFrame con las columnas a las cuales se le calcularan media, deviacion estandar, limite superior de la desviacion estandar, 
    limite_inferior de la desviacion estandar
  drop_columns: list
    Lista de columnas a las cuales no se les desea calcular media, deviacion estandar, limite superior de la desviacion estandar, 
    limite_inferior de la desviacion estandar

  Returns
  -------------
  dict
    Diccionario que posee media, deviacion estandar, limite superior de la desviacion estandar, 
    limite_inferior de la desviacion estandar de las columnas deseadas
  '''

  dft = pd.DataFrame.copy(df) #DataFrame Temporal
  columns = dft.columns
  if len(drop_columns) > 0:
    for column in drop_columns:
      columns = columns.drop(column)
  std_dict = {} #diccionario con la informacion de desviacion estandar
  for column in columns:
    column_values = drop_missing_values(dft[column].values)
    std_dict[column] = column_values
    values_mean = np.mean(column_values) #media
    std_dict[f"{column}_mean"] = values_mean 
    values_deviation = np.std(column_values) #desviacion estandar
    std_dict[f"{column}_deviation"] = values_deviation 
    std_dict[f"{column}_upper_std"] = values_mean + values_deviation #limite superior de la desviacion estandar
    std_dict[f"{column}_lower_std"] = values_mean - values_deviation #limite inferior de la desviacion estandar
  return std_dict


def __fill_missing_values_column(column_values:list, method: str) -> list:
  '''Funcion para llenar los valores faltantes de una columna con cierto metodo

  Parametros
  --------------
  columns_values: list
    Lista de valores de la columna que posee datos faltantes
  method str
    Metodo que se desea usar para llenar los valores faltantes de la columna, estos
    valores faltantes se pueden llenar mediante la medio la mediana
  
  Returns
  --------------
  list
    Lista con los valores faltantes de la columna reemplazados por la media o mediana
    de los valores de la columna.
  None
    Si el metodo dado no es "mean" o "median" se lanza un error y se retorna nulo
  '''

  try:
    assert(method == "mean" or method == "median"), "No defined method\nTry mean or median!"
    if method == "mean":
      values_mean = round(np.mean(drop_missing_values(column_values)), 1) #quito los datos faltantes para sacar la media de los valores
      filled_column_values = [values_mean if i == "" else i for i in column_values] #las posiciones que tengan un "" las reemplazo por la media
    elif method == "median":
      values_median =round(np.median(drop_missing_values(column_values)),1) #quito los datos faltantes para sacar la mediana de los valores
      filled_column_values = [values_median if i == "" else i for i in column_values] #las posiciones que tengan un "" las reemplazo por la mediana 
    return filled_column_values

  except AssertionError as error:
    print(error)
    return None


def fill_missing_values(df: pd.core.frame.DataFrame, columns: list, method: str):
  '''Funcion para llenar los valores faltantes de una columna de un DataFrame con cierto metodo

  Parametros
  -------------
  columns: list
    Nombre de las columnas a las cuales se les quiere aplicar el llenado de datos faltantes mediante
    cierto metodo
  method: str
    Metodo que se desea usar para llenar los valores faltantes de la columna, estos
    valores faltantes se pueden llenar mediante la medio la mediana

  Returns
  ------------
  pd.core.frame.DataFrame
    DataFrame en el que los valores faltantes de las columnas deseadas han sido reemplazados 
    por la media o mediana de la columna
  '''
  
  dft = pd.DataFrame.copy(df)
  for column in columns:
    dft[column] = __fill_missing_values_column(dft[column].values, method)
  return dft


def main():
    folder_direction = "https://raw.githubusercontent.com/spuertaf/SIME/main/macro_proyecto/datasets/bd_buses_1.csv" ##!!!!!!
    df = pd.read_csv(folder_direction)
    df = apply_in_rows(df, cleanse_rows, ["HORA"]) #limpieza de las filas
    dfc = pd.DataFrame.copy(df)
    columns = dfc.columns.drop("HORA")
    for column in columns:
        dfc[column] = dfc[column].apply(hex_to_value, column = column)
    dfc = fill_missing_values(dfc, ["RPM","LOAD"], "median")
    dfc = fill_missing_values(dfc, ["TEMP", "VEL"], "mean")
    print(dfc)
    
    


if __name__ == "__main__":
    main()