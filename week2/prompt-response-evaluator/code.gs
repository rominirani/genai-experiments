const modelNameToFlows = {
  "gemini-1.5-flash":"callGemini15Flash",
  "gemini-1.5-pro":"callGemini15Pro",
}

// Function to display the sidebar
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('AI Model Integration')
    .addItem('Show Sidebar', 'showSidebar')
    .addToUi();
}

// Function to show the Add-on UI
function showSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('Sidebar')
    .setTitle('AI Model Integration')
    .setWidth(300);
  
  SpreadsheetApp.getUi().showSidebar(html);
}

// Function to get the active range for live update
function getSelectedRange() {
  const activeRange = SpreadsheetApp.getActiveSpreadsheet().getActiveRange();
  if (activeRange) {
    return activeRange.getA1Notation();
  }
  return '';
}

// Function to handle model processing
function runModelProcessing(model1, model2, range, temperature) {
  // Implement the API call to the models here
  Logger.log(`Model 1: ${model1}, Model 2: ${model2}, Range: ${range}, Temperature: ${temperature}`);
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const promptData = sheet.getRange(range).getValues();
  Logger.log(`Prompt: ${promptData}`)
  // Iterate through rows
  for (let i = 0; i < promptData.length; i++) {
    const row = promptData[i];
    const currentRowNumber = i + sheet.getRange(range).getRow(); // Adjust for starting row

    // Iterate through columns within each row
    for (let j = 0; j < row.length; j++) {
      const cellValue = row[j];
      const currentColNumber = sheet.getRange(range).getColumn(); // Adjust for starting column

      // Do something with the cellValue
      Logger.log(`Sending off this prompt to model : ${model1} --> ${cellValue}`);
      resp1 = invokeDeployedModel(modelNameToFlows[model1], cellValue); 
      const cleanedResponse1 = resp1.replace(/([^"])\n/g, '$1\\n');
      result1 = JSON.parse(cleanedResponse1.slice(0,-2)).result;
      const outputCellModel1Response = sheet.getRange(currentRowNumber, currentColNumber+1); // Get cell at row 3, column 2
      outputCellModel1Response.setValue(result1); 

      Logger.log(`Sending off this prompt to model : ${model2} --> ${cellValue}`); 
      resp2 = invokeDeployedModel(modelNameToFlows[model2], cellValue); 
      const cleanedResponse2 = resp2.replace(/([^"])\n/g, '$1\\n');
      result2 = JSON.parse(cleanedResponse2.slice(0,-2)).result;
      const outputCellModel2Response = sheet.getRange(currentRowNumber, currentColNumber+2); // Get cell at row 3, column 2
      outputCellModel2Response.setValue(result2); 
    }
  }
}

//Function to show alert
function showAlert(msg) {
  Browser.msgBox(msg);
}

//Send the data to Genkit Flows deployed on Cloud Run
function invokeDeployedModel(modelName, prompt) {

  var url = `https://week1-ido3ocn3pq-uc.a.run.app/${modelName}`;

  //var url = 'https://us-central1-just-camera-319010.cloudfunctions.net/linkaccept';  // Replace with your function's URL
  var payload = {
    'data': prompt
  };

  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };

  var response = UrlFetchApp.fetch(url, options);
  return response.getContentText();
}

function test() {
  s = '{"result": "The capital of India is **New Delhi**. \n"}\n';
  const cleanedResponse = s.replace(/([^"])\n/g, '$1\\n'); 
  console.log(JSON.parse(cleanedResponse.slice(0,-2)).result);
}
