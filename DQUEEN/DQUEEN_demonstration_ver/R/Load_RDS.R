myValue <- lapply(file.path(getwd(),'/data',list.files(file.path(getwd(),'/data'))), readRDS)
for(i in 1:length(list.files(file.path(getwd(),'/data')))){
  assign(gsub('.RDS','',list.files(file.path(getwd(),'/data')))[i],myValue[[i]])
}
