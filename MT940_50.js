//-------------------------------------------------------------------------------
// Name:        Swift MT940/950 Generator
// Purpose:     Takes a specific csv file and converts it to
//              either an MT940 or MT950 swift message.
// Version:     1.0.0
// Author:      Thomas Edward Rudge
// Created:     2016-04-14
// Copyright:   (c) Thomas Edward Rudge 2016
// Licence:     GPL
//-------------------------------------------------------------------------------


// A function to pad out a string with a given character in either right or left direction
// padText = A string, padChar = A single character as a string, padLength = integer, padDirection = 'r' || 'l'
var paddify = function(padText, padChar, padLength, padDirection) {
   if (padText.length >= padLength) {
      return padText.slice(0, padLength)
   }
   if (padDirection === 'l') {
      return padText + padChar.repeat(padLength - padText.length);
   } else {
      return padChar.repeat(padLength - padText.length) + padText;
   }   
};


// A function that returns the current date in YYMMDD format
var todaysDate = function() {
   var dateObject = new Date();
   var dateString = '';
   
   dateString += String(dateObject.getFullYear()).slice(2);
   dateString += paddify(String(dateObject.getMonth() + 1), '0', 2, 'r');
   dateString += paddify(String(dateObject.getDate()), '0', 2, 'r');
   
   return dateString;
};


// This function takes an array of strings representing lines in a csv document and returns an 
// array of arrays that contain each lines cell values
// P.S. I know I should probably use a proper library like papaparse to do this. But papaparse 
// minified is only 2 KB smaller than this entire script. And the more you code, the more you learn
var csvParser = function(csvData) {
   var cellValue = ''; // The current cells value to be appended to cells
   var cells = [];     // A list of cell values for a given line to be appended to link
   var lines = [];     // A list of lines and their cell values as an array, for use later
   var dq = 0;         // A count of double quotes when assessing a cell's value
   
   for (var i = 0; i < csvData.length; i++) {             // Iterate over every line in the document (csvData array)
      for (var c of csvData[i]) {                     // Iterate over every character in the line
         if (c === '"') {                                // If a double quote add it to the count
            dq += 1;
         }
         
         if (c === ',') {                                // If a comma...
            if (dq === 0 || dq%2 === 0) {                // If the quote count is 0 or even the cell value is complete
               if (cellValue.startsWith('"') && cellValue.endsWith('"')) {
                  cellValue = cellValue.slice(1, -1)
               }
               cells.push(cellValue.replace(/""/g, '"'));// Add the cell value to the cells array
               cellValue = '';                           // Reset the cellValue for the next cell
               dq = 0;                                   // Reset the double quote count for the next cell
               continue
            }
         }
         cellValue += c;                                 // In all other cases add character to cell value string
      }
      
      if (cellValue.startsWith('"') && cellValue.endsWith('"')) {
         cellValue = cellValue.slice(1, -1)
      }
      // We do this next bit for the last cell in the line, because there is no comma at the end of the line
      cells.push(cellValue.replace(/""/g, '"'));// Add the cell value to the cells array
      cellValue = '';                           // Reset the cellValue for the next cell
      dq = 0;                   

      lines.push(cells);                                 // When line is finished, add the cells array to the lines array
      cells = [];                                        // Reset the cells array for the next line
   }
   return lines;
};


// This function takes a specific array and convert the data to its swift equivalent
var convertValues = function(xline, dtf) {
   var inScope = [5, 6, 11, 17, 18, 21];
   
   for (var i = 0; i < xline.length; i++) {
      switch(i) {
         case 5:  // Opening Balance Sign
         case 6:  // Opening Balance Type
         case 11: // Item Type
         case 17: // Closing Balance Sign
         case 18: // Closing Balance Type
         case 21: // Available Balance Sign
            // Convert signs and types to upper-case
            xline[i] = xline[i].toUpperCase();
            continue;
         case 8:  // Opening Balance
         case 12: // Item Amount
         case 20: // Closing Balance
         case 23: // Closing Available Balance
            // Remove thousand seps and replace decimal point with comma
            xline[i] = xline[i].replace(/,/g, '').replace('.', ',').replace('-','');
            continue;
         case 7:  // Opening Balance Date
         case 9:  // Item Value Date
         case 10: // Item Entry Date
         case 19: // Closing Balance Date
         case 22: // Closing Available Balance Date
            // Converts dates to YYMMDD based on date format setting
            switch(dtf) {
               case 'YYYYMMDD':
                  xline[i] = xline[i].slice(2,4) + xline[i].slice(5,7) + xline[i].slice(8,10);
                  break;
               case 'DDMMYYYY':
                  xline[i] = xline[i].slice(8, 10) + xline[i].slice(3, 5) + xline[i].slice(0, 2);
                  break;
               case 'MMDDYYYY':
                  xline[i] = xline[i].slice(8, 10) + xline[i].slice(0, 2) + xline[i].slice(3, 5);
                  break;
            }
      }
   }
   // Entry Dates have a shorter date format MMDD
   xline[10] = xline[10].slice(2, 6);
   return xline;
};


// This function will convert the users input into a swift MT9 message.
var genMt9 = function(activeFile, config) {
   // Split the csv data up into a array of strings
   activeFile = activeFile.split('\n');
   if (activeFile.length === 1) {
      document.getElementById("swift_output").value = 'Error: Insufficient Data';
      return;
   }
   // Get rid of the header if present.
   if (activeFile[0].toUpperCase().replace(/ /g, '').startsWith('SENDERBIC,RECEIVERBIC,ACCOUNTID,STMTNO,STMTPG,OPBALSIGN')) {
      activeFile.shift();
   }
   // Get rid of blank lines
   while (activeFile[activeFile.length - 1].replace(/ /g, '') == '') {
      activeFile.pop();
   }
   // Parse the CSV Data
   activeFile = csvParser(activeFile);
   // If message type is set to auto, check to see whether Ref4 (:86:) data is
   // present and set to MT940 if so. Else strip the MT prefix from the type.
   if (config['msgTyp'] === 'Auto') {
      var tmp = 0;
      
      for (var i = 0; i < activeFile.length; i++) {
         tmp += activeFile[i][25].length;
      }
      
      if (tmp > 0) {
         config['msgTyp'] = '940';
      } else {
         config['msgTyp'] = '950';
      }
   } else {
      config['msgTyp'] = config['msgTyp'].slice(2);
   }
   // This will keep track of the last lines details...
   // so that we know when to close a statement page or message
   var prevLine = { 
      account : '',
      sendbic : '',
      recvbic : '',
      stmtno  : '',
      stmtpg  : '',
      ccy     : '',
      cbalsgn : '',
      cbaltyp : '',
      cbaldte : '',
      cbal    : '',
      abalsgn : '',
      abaldte : '',
      abal    : ''
   };   
   
   var trn = 0;              // Used to numerate TRNs when none present
   var lastLine = null;      // Used to keep track of last line processed
   var outputString = '';    // Where the cumulated swift data will be written to
   var today = todaysDate(); // Today's date in YYMMDD format
   
   for (var i = 0; i < activeFile.length; i++) {
      var zline = ''; // This string that will be appended to outputString
      // Check the number of columns is correct
      if (activeFile[i].length !== 27) {
         document.getElementById("swift_output").value = 'Error: Bad column count on line ' + String(i + 1);
         return;
      }
      // Convert values to swift equivalent
      activeFile[i] = convertValues(activeFile[i], config['dtf']);
      // Check whether the previous message needs to be closed
      if ((prevLine['stmtpg'] !== activeFile[i][4] || prevLine['account'] !== activeFile[i][2]) && prevLine['account'] !== '') {
         outputString += ':62' + prevLine['cbaltyp'] + ':' + prevLine['cbalsgn'] + prevLine['cbaldte'] + prevLine['ccy'] + prevLine['cbal'] + '\n';
         if (prevLine['abalsgn'] !== '') {
            outputString += ':64:' + prevLine['abalsgn'] + prevLine['abaldte'] + prevLine['ccy'] + prevLine['abal'] + '\n';
         }
      }
      // Check whether it is a new message
      if (prevLine['sendbic'] !== activeFile[i][0].toUpperCase() || prevLine['recvbic'] !== activeFile[i][1].toUpperCase()) {
         if (prevLine['sendbic'] !== '') {
            // New message. Close the last one
            if (config['chk'].replace(/ /g, '') !== '') {
               outputString += '-}{5:{CHK:' + config['chk'] + '}}\n';
            } else {
               outputString += '-}{5:}\n';
            }
         }
         // Open the next message
         // Create the Basic Header Block
         outputString += '{1:' + config['appId'] + config['srvId'] + paddify(activeFile[i][0], 'X', 12, 'l') + config['sessn'] + config['sqncn'] + '}';
         // Create Application Header Block
         if (config['drctn'] === 'I') {// Inward
            outputString += '{2:I' + config['msgTyp'] + paddify(activeFile[i][1], 'X', 12, 'l') + config['prrty'] + config['dlvm'] + config['obslc'] + '}';
         } else {// Outward
            if (config['mir'].replace(/ /g, '') === '') {
               //Auto generate MIR
               config['mir'] = today + paddify(activeFile[i][0], 'X', 12, 'l') + config['sessn'] + config['sqncn'];
            }
            outputString += '{2:O' + config['msgTyp'] + config['inpt'] + config['mir'] + config['outd'] + config['outt'] + config['prrty'] +'}';
         }
         //Create User Header Block
         // Add Bank Priority Code F113 if present
         if (config['prtyc'] !== '') {
            config['prtyc'] = '{113:' + paddify(config['prtyc'], '0', 4, 'r') + '}';
         }
         outputString += '{3:' + config['prtyc'] + '{118:' + config['mur'] + '}{4:\n';
      }
      // Check to see whether a new statement page should be opened
      if (prevLine['stmtpg'] !== activeFile[i][4] || prevLine['account'] !== activeFile[i][2]) {
         // Check for TRN, and use default if not present
         if (activeFile[i][26].replace(/ /g, '') === '') {// No TRN
            outputString += ':20:MT94050GEN' + paddify(String(trn), '0', 6, 'r') + '\n';
            trn += 1;
         } else {
            outputString += ':20:' + activeFile[i][26] + '\n';
         }
         // Add the account
         outputString += ':25:' + activeFile[i][2] +'\n';
         // Add statement page and number
         outputString += ':28C:' + paddify(activeFile[i][3], '0', 5, 'r') + '/' + paddify(activeFile[i][4], '0', 5, 'r') + '\n';
         // Add opening balance
         outputString += ':60' + activeFile[i][6] + ':' + activeFile[i][5] + activeFile[i][7] + activeFile[i][24] + activeFile[i][8] + '\n';
      }
      // Now add the item line
      outputString += ':61:' + activeFile[i][9] + activeFile[i][10] + activeFile[i][11] + activeFile[i][12] + activeFile[i][13] + activeFile[i][14] + '//' + activeFile[i][15] + '\n';
      // If Ref 3 (Sub field 9) present, add it.
      if (activeFile[i][16].replace(/ /g, '') !== '') {
         outputString += activeFile[i][16] + '\n';
      }
      // If message type is 940 and Ref4 (Field 86) present, add it.
      if (config['msgTyp'] === '940' && activeFile[i][25].replace(/ /g, '') !== '') {
         outputString += ':86:' + activeFile[i][25] + '\n';
      }
      // Set comparative values for next row
      prevLine['account'] = activeFile[i][2];
      prevLine['sendbic'] = activeFile[i][0];
      prevLine['recvbic'] = activeFile[i][1];
      prevLine['stmtno']  = activeFile[i][3];
      prevLine['stmtpg']  = activeFile[i][4];
      prevLine['ccy']     = activeFile[i][24];
      prevLine['cbalsgn'] = activeFile[i][17];
      prevLine['cbaltyp'] = activeFile[i][18];
      prevLine['cbaldte'] = activeFile[i][19];
      prevLine['cbal']    = activeFile[i][20];
      prevLine['abalsgn'] = activeFile[i][21];
      prevLine['abaldte'] = activeFile[i][22];
      prevLine['abal']    = activeFile[i][23];
   }
   // Close the very last row of the file
   i -= 1; // Because it would have iterated beyond the last index to break the for loop
   outputString += ':62F:' + activeFile[i][17] + activeFile[i][19] + activeFile[i][24] + activeFile[i][20] + '\n';
   // Write available balance if present.
   if (activeFile[i][21] !== '') {
      outputString += ':64:' + activeFile[i][21] + activeFile[i][22] + activeFile[i][24] + activeFile[i][23] + '\n';
   }
   // If checksum value write it, else close message
   if (config['chk'].replace(/ /g, '') !== '') {
      outputString += '-}{5:{CHK:' + config['chk'] + '}}';
   } else {
      outputString += '-}{5:}';
   }
   // Now display the results on screen
   document.getElementById("swift_output").value = outputString;
};


// This function will get the values from the user input area and
// the advanced options, and then pass them to the main function
var startSwiftScript = function() {
   // Cover my arse
   var legal = confirm("I (the author of this program) make no guarantees and accept \
no responsibility for any damages or loss (physical, material, financial, or otherwise), \
corruption of or loss of data, caused by the use of this program or its outputs. You \
use the output of this program at your own risk.")
   if (!legal) {
      return;
   }
   // Get the setting values and convert them into an object (dictionary)
   var eleVals = document.getElementsByName("genops");
   var genOps = [];
   
   for (var i = 0; i < eleVals.length; i++) {
      genOps.push(eleVals[i].value);
   }
   // Full details of swift header block structure can be found here...
   // http://www.ibm.com/support/knowledgecenter/SSBTEG_4.3.0/com.ibm.wbia_adapters.doc/doc/swift/swift72.htm%23HDRI1023624
   var genOpsOb = {
      msgTyp: genOps[0], // Message type          : 940 or 950
      dtf:    genOps[1], // Date Format           : YYYYMMDD or DDMMYYYY or MMDDYYYY
      appId:  genOps[2], // Application ID        : A or F or L
      srvId:  genOps[3], // Service ID            : 01 or 21
      sessn:  genOps[4], // Session Number        : nnnn
      sqncn:  genOps[5], // Sequence Number       : nnnnnn
      drctn:  genOps[6], // Direction             : I or O
      prrty:  genOps[7], // Message Priority      : S or N or U
      obslc:  genOps[8], // Obsolescence period   : 003 or 020
      dlvm:   genOps[9], // Delivery Monitoring   : 1 or 2 or 3
      inpt:   genOps[10],// Input Time            : hhmm
      outt:   genOps[11],// Output Time           : hhmm
      outd:   genOps[12],// Output Date           : yymmdd
      mir:    genOps[13],// Message Input Ref     : String
      mur:    genOps[14],// Message User Ref      : String
      prtyc:  genOps[15],// Banking Priority Code : nnnn
      chk:    genOps[16] // Checksum              : String
   };
   // Replace 0 flags with empty strings
   if (genOpsOb['obslc'] === '0') {
      genOpsOb['obslc'] = '';
   }
   
   if (genOpsOb['dlvm'] === '0') {
      genOpsOb['dlvm'] = '';
   } 
   // The user input
   var inputs = document.getElementById("swift_input").value;
   
   if (inputs !== '' && 
       inputs.indexOf('CSV data should be pasted in here.') === -1 && 
       inputs.includes(',')) {
      // Start the process
      document.getElementById("swift_output").value = 'This wont take long';
      genMt9(inputs, genOpsOb);
   } else {
      document.getElementById("swift_output").value = 'Error: Invalid Input';
   }
};