param location string
param baseName string
param storageSku string
param deployCustomVisionFallback bool

var contentUnderstandingAccountName = toLower('${baseName}cu${uniqueString(resourceGroup().id)}')
var trainingAccountName = toLower('${baseName}tr${uniqueString(resourceGroup().id)}')
var predictionAccountName = toLower('${baseName}pr${uniqueString(resourceGroup().id)}')
var blobContainerName = 'images'
var shortBaseNameForStorage = toLower(take(baseName, 9))
var shortBaseNameForKv = toLower(take(baseName, 9))
var storageAccountNameSafe = '${shortBaseNameForStorage}st${take(uniqueString(resourceGroup().id), 13)}'
var keyVaultNameSafe = '${shortBaseNameForKv}kv${take(uniqueString(resourceGroup().id), 12)}'

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountNameSafe
  location: location
  sku: {
    name: storageSku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource imagesContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: blobContainerName
  properties: {
    publicAccess: 'None'
  }
}

resource contentUnderstanding 'Microsoft.CognitiveServices/accounts@2025-12-01' = {
  name: contentUnderstandingAccountName
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

resource customVisionTraining 'Microsoft.CognitiveServices/accounts@2025-12-01' = if (deployCustomVisionFallback) {
  name: trainingAccountName
  location: location
  kind: 'CustomVision.Training'
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

resource customVisionPrediction 'Microsoft.CognitiveServices/accounts@2025-12-01' = if (deployCustomVisionFallback) {
  name: predictionAccountName
  location: location
  kind: 'CustomVision.Prediction'
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultNameSafe
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenant().tenantId
    enabledForDeployment: false
    enabledForTemplateDeployment: false
    enabledForDiskEncryption: false
    publicNetworkAccess: 'Enabled'
    enableRbacAuthorization: true
  }
}

output storageAccountName string = storage.name
output blobContainerName string = imagesContainer.name
output contentUnderstandingAccountName string = contentUnderstanding.name
output trainingAccountName string = deployCustomVisionFallback ? customVisionTraining.name : ''
output predictionAccountName string = deployCustomVisionFallback ? customVisionPrediction.name : ''
output keyVaultName string = keyVault.name
