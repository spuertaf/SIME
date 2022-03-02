bd_route = "C:\\Users\\Admin\\Desktop\\SIME\\macro_proyecto\\datasets\\bd_clean_buses_1.csv" #ruta donde esta mi csv 
df = read.csv(bd_route)


#hallar amplitud de los intervalos
k = 7 #numero de intervalos que se desean
amplitud = ((max(df$RPM) - min(df$RPM)) / k)
limites = seq(min(df$RPM), max(df$RPM), by= amplitud)
limites = round(limites, 1)
intervalos = cut(x = df$RPM, breaks = limites, right = F)
#hacer la tabla de RPM por intervalos
rpm_table = table(intervalos)
rpm_table
hist(df$RPM, breaks = limites)
barplot(rpm_table)