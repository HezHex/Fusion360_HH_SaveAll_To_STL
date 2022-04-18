# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from .lib import fusion360utils as futil


import adsk.core, adsk.fusion, adsk.cam, traceback

handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
        # Create a button command definition.
        buttonSaveAll = cmdDefs.addButtonDefinition('SaveAllButtonDefId', 
                                                   'Save Bodies To stl', 
                                                   'Create an stl for any selected bodies',
                                                   './Resources/SaveAll')
       
        # Connect to the command created event.
        SaveAllCommandCreated = SaveAllEventHandler()
        buttonSaveAll.commandCreated.add(SaveAllCommandCreated)
        handlers.append(SaveAllCommandCreated)
        
        # Get the ADD-INS panel in the model workspace. 
        addInsPanel = ui.allToolbarPanels.itemById('MakePanel')
      
        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(buttonSaveAll)


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class SaveAllEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command

        # Connect to the execute event.
        onExecute = SaveAllExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

class SaveAllExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        # Code to react to the event.
        app = adsk.core.Application.get()
        ui  = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        exportMgr = design.exportManager
        outDir = ''
        SelItems = len(ui.activeSelections)

        if SelItems <= 0:
         ui.messageBox("No Bodies selected!")
         return
        else:
         ui.messageBox(str(SelItems) + " Bodies selected!")

        msg = ''

        # Set styles of file dialog.
        folderDlg = ui.createFolderDialog()
        folderDlg.title = 'Choose Target Folder' 
        
        # Show folder dialog
        dlgResult = folderDlg.showDialog()
        if dlgResult == adsk.core.DialogResults.DialogOK:
            msg += '\nSelected Folder: {}'.format(folderDlg.folder)
            outDir = folderDlg.folder
        else:
            ui.messageBox("No folder Selected!")
            return
            
        ui.messageBox(msg)

        result = ''
        for selection in ui.activeSelections:
            selectedEnt = selection.entity
            if selectedEnt.objectType == adsk.fusion.BRepBody.classType():

               fileName = outDir + "/" + selectedEnt.name
               stlExportOptions = exportMgr.createSTLExportOptions(selectedEnt, fileName)
               stlExportOptions.sendToPrintUtility = False
               exportMgr.execute(stlExportOptions)

               result += 'Saved Body: ' + selectedEnt.name + '\n'
            else:
                result += 'Other selection: ' + selectedEnt.objectType + '\n'

            ui.messageBox(result, 'Saving Report')



def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('SaveAllButtonDefId')
        if cmdDef:
            cmdDef.deleteMe()
            
        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addinsPanel.controls.itemById('SaveAllButtonDefId')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	
