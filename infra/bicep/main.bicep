targetScope = 'resourceGroup'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Prefix used for all resource names')
param baseName string = 'logoverifpoc'

@description('Storage account SKU')
param storageSku string = 'Standard_LRS'

@description('Deploy optional Custom Vision resources as fallback backend')
param deployCustomVisionFallback bool = false

module core './modules/core-resources.bicep' = {
  params: {
    location: location
    baseName: baseName
    storageSku: storageSku
    deployCustomVisionFallback: deployCustomVisionFallback
  }
}

output storageAccountName string = core.outputs.storageAccountName
output blobContainerName string = core.outputs.blobContainerName
output contentUnderstandingAccountName string = core.outputs.contentUnderstandingAccountName
output trainingAccountName string = core.outputs.trainingAccountName
output predictionAccountName string = core.outputs.predictionAccountName
output keyVaultName string = core.outputs.keyVaultName
