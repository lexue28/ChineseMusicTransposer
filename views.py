import re
from flask import Blueprint, flash, redirect, render_template, request, jsonify, url_for
import pandas as pd
#define all views here
views = Blueprint(__name__, "views")

@views.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        convertButtonLtoNClicked = request.form.get("convertButtonLtoN")
        transposeButtonClicked = request.form.get("transposeButton")
        convertButtonNtoLClicked = request.form.get("convertButtonNtoL")
        if convertButtonLtoNClicked is not None:
            # convert
            letterNotes = request.form["letterNotes"]
            currentKey = request.form["currentKey"]
            return redirect(url_for("views.convertLtoN", letterNotes = letterNotes, currentKey = currentKey))      

        elif transposeButtonClicked is not None:
            # transpose
            numberNotes = request.form["numberNotes"]
            startKey = request.form["startKey"]
            endKey = request.form["endKey"]
            return redirect(url_for("views.transposeNumbers", numberNotes = numberNotes, startKey = startKey, endKey = endKey)) 
        
        elif convertButtonNtoLClicked is not None:
            print("got into n to l clicked")
            numberNotes = request.form["numberNotes"]
            currentKey = request.form["currentKey"]
            return redirect(url_for("views.convertNtoL", numberNotes = numberNotes, currentKey = currentKey))
        
    else:
        return render_template("index.html")

def createConversionChart(keySignature):
    conversionChart = {}
    chineseNumber = 1  #key note is equal to 1, ex. G key then G = 1

    for note in keySignature:  #iterate through all 7 valid notes
        conversionChart[note] = chineseNumber  #add a new key-value (note, number)
        chineseNumber = chineseNumber + 1  #move on to assign next number
    return conversionChart

# control sharps and flats, oddNote is not in conversion chart dictionary, keySig is the keysig of the key
#ex. b flat signature, B
def accidentals(conversionChart, oddNote):
    sharp = False
    flat = False
    neutral = False
    if '#' in oddNote:
        sharp = True
    elif '♭' in oddNote:
        flat = True
    else:
        neutral = True
    noAccidentals = "".join(filter(str.isalpha, oddNote))

    for i in conversionChart:
        #if an element contains the note, get the index
        if noAccidentals in i:
            if sharp == True:
                #if oddnote has a sharp and the conversion chart has a flat
                if '♭' in i:
                    conversionChart[oddNote] = str(conversionChart[i] + 1)
                else:
                    #oddnote has a flat and if conversion chart corresponding note is neutral
                    conversionChart[oddNote] = str(conversionChart[i]) + '#'
            if flat == True:
                #if oddnote has a flat and the conversion chart has a sharp
                if '#' in i:
                    conversionChart[oddNote] = str(conversionChart[i] - 1)
                else:
                    #oddnote has a sharp and if conversion chart corresponding note is neutral
                    conversionChart[oddNote] = str(conversionChart[i]) + '♭'
            if neutral == True:
                if '#' in i:
                    conversionChart[oddNote] = str(conversionChart[i]) + '♭'
                if '♭' in i:
                    conversionChart[oddNote] = str(conversionChart[i]) + '#'
            return conversionChart


@views.route('/convertLtoN', methods=["GET", "POST"])
def convertLtoN():
    if request.method == "POST":
        backButtonClicked = request.form.get("backButton")
        if backButtonClicked is not None:
            # if back button is clicked, redirect to home page
            return redirect(url_for("views.home"))
    
    currentKey = request.args["currentKey"].upper()  #current key we are in
    validKeys = [
        'C', 'G', 'D', 'A', 'E', 'F', 'B♭', 'E♭', 'A♭', 'C♭', 'B', 'G♭', 'F#', 'D♭', 'C#'
    ]
    print(currentKey)
    print(validKeys)
    if currentKey in validKeys and currentKey is not None:
        print(currentKey, "Key selected! :)")
    else:
       print("Invalid key, please try again")
       flash("Invalid key, please try again")
       return redirect(url_for("views.home"))      

    
    letterNotes = request.args['letterNotes'].upper().split()
    letterNotesString = str(request.args['letterNotes'].upper())
    normalString="".join(ch for ch in letterNotesString if ch.isalnum())
    print("this is after filter", normalString)
    if len(letterNotes) == 1 and len(normalString) > 1:
        flash("Please put spaces between notes")
        return redirect(url_for("views.home"))  

        # if contains an integer
    if any(chr.isdigit() for chr in letterNotesString):
        flash("Please input only valid letters, # or ♭ also accepted")
        return redirect(url_for("views.home")) 
    
    filename = "static/keySignatures.csv" 
    keySignatures = pd.read_csv(filename, header=0)
    
    convertedNotes = []
    #dictionary to hold the note and the corresonding number. ex. (G = 1)
    conversionChart = createConversionChart(keySignatures[currentKey])
    print(conversionChart)

    for i in letterNotes:
        if conversionChart.get(i) is None:
            conversionChart = accidentals(conversionChart, i)
            print(conversionChart[i])
        convertedNotes.append(conversionChart[i])
        

    print("Converted notes:", convertedNotes)
    print("\n")  #line break for neatness

    # display original notes and converted notes
    return render_template("letterToNumber.html", key=currentKey, notes=letterNotes, newNotes=convertedNotes)

@views.route('/transposeNumbers', methods=["GET", "POST"])
def transposeNumbers():
    if request.method == "POST":
        backButtonClicked = request.form.get("backButton")
        if backButtonClicked is not None:
            # if back button is clicked, redirect to home page
            return redirect(url_for("views.home"))
    
    startKey = request.args["startKey"].upper()  # current key we are in
    endKey = request.args["endKey"].upper() # target key
    validKeys = [
        'C', 'G', 'D', 'A', 'E', 'F', 'B♭', 'E♭', 'A♭', 'C♭', 'B', 'G♭', 'F#', 'D♭', 'C#'
    ]
    print("Current key is", startKey)
    print("End key is", endKey)
    # check if both keys are valid
    if startKey in validKeys and startKey is not None and endKey in validKeys and endKey is not None:
        print(startKey, "starting key selected! :)")
        print(endKey, "ending key selected! :)")
    else:
       print("Invalid key(s), please try again")
       flash("Invalid key(s), please try again")
       return redirect(url_for("views.home"))      

    # split numbers apart based on spaces
    numberNotes = request.args['numberNotes'].upper().split()
    print("Notes to transpose:", numberNotes)
    numberNotesString = str(request.args['numberNotes'].upper())
    normalString="".join(ch for ch in numberNotesString if ch.isalnum())
    print("this is after filter", normalString)
    if len(numberNotes) == 1 and len(normalString) > 1:
        flash("Please put spaces between notes")
        return redirect(url_for("views.home"))  
    
    # if contains a letter
    if any(c.isalpha() for c in numberNotesString):
        flash("Please input only numbers (1-7), # or ♭ also accepted")
        return redirect(url_for("views.home")) 
    
    filename = "ChineseMusicTransposer\static\keySignatures.csv" 
    keySignatures = pd.read_csv(filename, header=0)

    # create conversion charts
    startKeyChart = createConversionChart(keySignatures[startKey])
    endKeyChart = createConversionChart(keySignatures[endKey])
    print("start Key signature", startKeyChart)
    print("end Key signature", endKeyChart)

    transposedNotes = []
    transposingChart = {}

    for i in numberNotes:
      #find corresponding letter for a number
      # TODO: CHECK IF i IS IN STARTKEYCHART values, IF NOT ADD
        
        if isInDictValue(startKeyChart, i) == False:
            print(i, "is not in conversion chart values currently")
            startKeyChart = accidentalsNumber(startKeyChart, i)
            print("New starting conversion Chart:", startKeyChart)
            #print(startKeyChart[i])

        letter = getKeyByValue(startKeyChart, i)
        print("corresponding letter to i", letter)
      
        if endKeyChart.get(letter) is None:
        #if not in chart, then find what letter would be in chart
      	    endKeyChart = accidentals(endKeyChart, letter)
        
        transposingChart[i] = endKeyChart.get(letter)
        transposedNotes.append(endKeyChart.get(letter))
        
    print("Transposition chart:", transposingChart)
    print("Transposed notes:", transposedNotes)
    print("\n")  #line break for neatness()

    # display original notes and transposed notes
    return render_template("transposeNumbers.html", startKey=startKey, endKey=endKey, notes=numberNotes, newNotes=transposedNotes)

@views.route('/convertNtoL', methods=["GET", "POST"])
def convertNtoL():
    if request.method == "POST":
        backButtonClicked = request.form.get("backButton")
        if backButtonClicked is not None:
            # if back button is clicked, redirect to home page
            return redirect(url_for("views.home"))
    
    currentKey = request.args["currentKey"].upper()  #current key we are in
    validKeys = [
        'C', 'G', 'D', 'A', 'E', 'F', 'B♭', 'E♭', 'A♭', 'C♭', 'B', 'G♭', 'F#', 'D♭', 'C#'
    ]
    print(currentKey)
    print(validKeys)
    if currentKey in validKeys and currentKey is not None:
        print(currentKey, "Key selected! :)")
    else:
       print("Invalid key, please try again")
       flash("Invalid key, please try again")
       return redirect(url_for("views.home"))    
     
    numberNotes = request.args['numberNotes'].split()
    print(numberNotes)
    numberNotesString = str(request.args['numberNotes'])
    normalString="".join(ch for ch in numberNotesString if ch.isalnum())
    print("this is after filter", normalString)
    if len(numberNotes) == 1 and len(normalString) > 1:
        flash("Please put spaces between notes")
        return redirect(url_for("views.home"))  
    
    # if contains a letter
    if any(c.isalpha() for c in numberNotesString):
        flash("Please input only numbers (1-7), # or ♭ also accepted")
        return redirect(url_for("views.home")) 
    filename = "ChineseMusicTransposer\static\keySignatures.csv" 
    keySignatures = pd.read_csv(filename, header=0)
    
    convertedNotes = []
        #dictionary to hold the note and the corresonding number. ex. (G = 1)
    conversionChart = createConversionChart(keySignatures[currentKey])
    print(conversionChart)

    for i in numberNotes:
        # if a note to transpose is not in the conversion chart
        if isInDictValue(conversionChart, i) == False:
            conversionChart = accidentalsNumber(conversionChart, i)
        # note is in the corresponding chart, then append the letter
        print("conversion ntol", conversionChart)
        convertedNotes.append(getKeyByValue(conversionChart, i))
        

    print("Converted notes:", convertedNotes)
    print("\n")  #line break for neatness

    # display original notes and converted notes
    return render_template("numberToLetter.html", key=currentKey, notes=numberNotes, newNotes=convertedNotes)

    


def isInDictValue(dict, value):
    value = str(value)
    for i in dict:
        dictValue = str(dict.get(i))
        if dictValue == value:
            return True
    return False


def getKeyByValue(dict, value):
    value = str(value)
    for i in dict:
        dictValue = str(dict.get(i))
        if dictValue == value:
            key = i
            return key



# control sharps and flats, oddNote is not in conversion chart dictionary, keySig is the keysig of the key
#ex. b flat signature, B
# adds the corresponding note to a number
def accidentalsNumber(transposingChart, oddNumber):
    sharp = False
    flat = False
    neutral = False
    if '#' in oddNumber:
        sharp = True
    elif '♭' in oddNumber:
        flat = True
    else:
        neutral = True
    # filters the number so # and flat go away
    number = re.findall(r'\d+', oddNumber)
    # take number out of the list
    noAccidentals = number[0]
    for i in transposingChart.values():
        #if an element contains the note, get the index
        if noAccidentals in str(i):
            correspondingNote = getKeyByValue(transposingChart, i)
            if sharp == True:
                #if oddNumber has a sharp and the transposition chart has a flat
                if '♭' in correspondingNote:
                    #no AccidentalsNote = the note i without a flat sign
                    noAccidentalsNote = "".join(filter(str.isalpha, correspondingNote))
                    transposingChart[noAccidentalsNote] = oddNumber
                else:
                    #oddnote has a flat and if conversion chart corresponding note is neutral
                    transposingChart[correspondingNote + "#"] = oddNumber
            if flat == True:
                #if oddNumber has a flat and the transposition chart has a sharp
                if '#' in correspondingNote:
                    #no AccidentalsNote = the note i without a flat sign
                    noAccidentalsNote = "".join(filter(str.isalpha, correspondingNote))
                    transposingChart[noAccidentalsNote] = oddNumber
                else:
                    #oddnote has a sharp and if conversion chart corresponding note is neutral
                    transposingChart[correspondingNote + "♭"] = oddNumber
            if neutral == True:
                print("Error", oddNumber, "cannot be neutral")

            print(transposingChart)
            return transposingChart
