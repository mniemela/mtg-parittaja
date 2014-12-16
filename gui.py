# -*- coding: latin-1 -*-
import wx
import wx.lib.intctrl
import parittaja

class Form(wx.Panel):
    '''Kaikkee hassua'''
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        self.createControls()
        self.bindEvents()
        self.doLayout()
        
    def createControls(self):
        raise NotImplementedError
    
    def bindEvents(self):
        raise NotImplementedError
    
    def doLayout(self):
        raise NotImplementedError

class Tournament(Form):
    
    def doLayout(self):
        boxSizer = wx.BoxSizer(orient = wx.HORIZONTAL)
        gridSizer = wx.FlexGridSizer(rows = 5, cols = 2, vgap = 10, hgap = 10)
        
        expandOption = dict(flag = wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0,0), noOptions)
        
        for control, options in \
                [(self.roundLabel, noOptions),
                 (self.roundCtrl, expandOption),
                 (self.draftCheckBox, noOptions),
                 (self.eliminationCheckBox, noOptions),
                 (self.seatingsButton, noOptions),
                 (wx.StaticText(self, label = ""), noOptions),
                 (self.nameLabel, noOptions),
                 (self.nameTextCtrl, expandOption),
                 (self.droppedCheckBox, noOptions),
                 (self.saveButton, noOptions),
                 (self.addButton, noOptions),
                 (self.deleteButton, dict(flag = wx.ALIGN_CENTER))]:
            gridSizer.Add(control, **options)
        
        for control, options in \
                [(gridSizer, dict(border = 5, flag = wx.ALL)),
                 (self.playersList, dict(border = 5, flag = wx.ALL | wx.EXPAND,
                    proportion = 1))]:
            boxSizer.Add(control, **options)
        
        self.SetSizerAndFit(boxSizer)
        
    def createControls(self):
        self.nameLabel = wx.StaticText(self, label = "Player name:")
        self.nameTextCtrl = wx.TextCtrl(self, value = "Name")
        self.droppedCheckBox = wx.CheckBox(self, label = "Dropped?")
        self.roundLabel = wx.StaticText(self, label = "Rounds:")
        self.roundCtrl = wx.lib.intctrl.IntCtrl(self, value = 0)
        self.saveButton = wx.Button(self, label = "Save")
        self.addButton = wx.Button(self, label = "Add")
        self.deleteButton = wx.Button(self, label = "Delete")
        self.playersList = wx.ListBox(self, style = wx.LB_SINGLE)
        self.draftCheckBox = wx.CheckBox(self, label = "Draft?")
        self.eliminationCheckBox = wx.CheckBox(self, label = "Single elimination?")
        self.seatingsButton = wx.Button(self, label = "Generate seatings")
        
    def bindEvents(self):
        for control, event, handler in \
            [(self.roundCtrl, wx.EVT_TEXT, self.onRoundEntered),
             (self.saveButton, wx.EVT_BUTTON, self.onSave),
             (self.droppedCheckBox, wx.EVT_CHECKBOX, self.onDropped),
             (self.addButton, wx.EVT_BUTTON, self.onAdd),
             (self.deleteButton, wx.EVT_BUTTON, self.onDelete),
             (self.playersList, wx.EVT_LISTBOX, self.onSelection),
             (self.draftCheckBox, wx.EVT_CHECKBOX, self.tournamentSettings),
             (self.eliminationCheckBox, wx.EVT_CHECKBOX, self.tournamentSettings),
             (self.seatingsButton, wx.EVT_BUTTON, self.generateSeatings)]:
            control.Bind(event, handler)
    
    def setTournament(self, tournament_, match_form):
        self.otherForm = match_form
        self.tournament = tournament_
        self.playersList.Clear()
        self.saveButton.Disable()
        self.deleteButton.Disable()
        self.droppedCheckBox.Disable()
        self.addButton.Enable()
        self.roundCtrl.Clear()
        self.nameTextCtrl.Clear()
        self.draftCheckBox.Enable()
        self.eliminationCheckBox.Enable()
        self.seatingsButton.Disable()
        
        self.started = False
        
    def generateSeatings(self, event):
        if self.eliminationCheckBox.GetValue() and self.draftCheckBox.GetValue() and self.playersList.GetCount() != 8:
            dlg = wx.MessageDialog(self, "Single elimination draft is only supported for 8 players!",  "Error",
            pos = self.GetPosition(), style = wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, "Generate seatings?", "?",
            pos = self.GetPosition(), style = wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:        
            self.tournament.seatings()
            players = self.playersList.GetStrings()
            self.playersList.Clear()
            for p in players:
                self.playersList.Append(p + ", seat: " + str(self.tournament.pelaajanSeating(p)))
            self.playersList.SetSelection(self.playersList.GetCount() - 1)
            self.onSelection(0)
            self.addButton.Disable()
            self.draftCheckBox.Disable()
            self.seatingsButton.Disable()
            if self.draftCheckBox.GetValue():
                self.eliminationCheckBox.Disable()
        dlg.Destroy()
        
    def tournamentSettings(self, event):
        if self.draftCheckBox.GetValue():
            self.seatingsButton.Enable()
        else: 
            self.seatingsButton.Disable()
        self.tournament.single_elimination = self.eliminationCheckBox.GetValue()
        self.tournament.draft = self.draftCheckBox.GetValue()

        
    def nameTooLongDialog(self):
        dlg = wx.MessageDialog(self, "Player name is too long!",  "Error",
            pos = self.GetPosition(), style = wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
    
    def forbiddenCharactersDialog(self):
        dlg = wx.MessageDialog(self, "Only alphabets and spaces are allowed in name!",  "Error",
            pos = self.GetPosition(), style = wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
    
    def onAdd(self, event):
        name = self.nameTextCtrl.GetLineText(0)
        if not name.replace(" ", "").isalpha():
            self.forbiddenCharactersDialog()
            return
        if len(name) > 25:
            self.nameTooLongDialog()
            return
        try:
            self.tournament.lisaaPelaaja(name)
            self.playersList.Append(name)
            self.playersList.SetSelection(self.playersList.GetCount() - 1)
            self.onSelection(0)
        except parittaja.OmaPoikkeus as e:
            temp = ""
            print str(e)
            if str(e) == "'Voi olla vain yksi Bye!'":
                temp = "There can be only one Bye!"
            else:
                temp = "Player already exists!"
            dlg = wx.MessageDialog(self, temp, "Error", pos = self.GetPosition(), 
                style = wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
    
    def onSave(self, event):
        oldname = self.playersList.GetStringSelection().split(",")[0]
        newname = self.nameTextCtrl.GetLineText(0)
        seating = self.tournament.pelaajanSeating(oldname)
        if not newname.replace(" ", "").isalpha():
            self.forbiddenCharactersDialog()
            return
        if len(newname) > 25:
            self.nameTooLongDialog()
            return
        try:
            self.tournament.paivitaPelaaja(oldname, newname, self.droppedCheckBox.GetValue())
            if self.tournament.seatingsit:
                self.playersList.SetString(self.playersList.GetSelection(), newname + ", seat: " + str(seating))
            else:
                self.playersList.SetString(self.playersList.GetSelection(), newname)
        except parittaja.OmaPoikkeus as e:
            temp = ""
            if str(e) == "'Samanniminen pelaaja on olemassa'":
                temp = "Player with that name already exists!"
            elif str(e) == "'Voi olla vain yksi Bye!'":
                temp = "There can be only one Bye!"
            else:
                temp = "Internal error"
            dlg = wx.MessageDialog(self, temp, "Error", pos = self.GetPosition(), 
                style = wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
    
    def onDelete(self, event):
        #ei jaksa tehdä poikkeuskäsittelyä, poikkeus voi lentää
        #vain jos ohjelma bugaa, ainakin huomaa sen sitten
        self.tournament.poistaPelaaja(self.playersList.GetStringSelection())
        self.playersList.Delete(self.playersList.GetSelection())
        if self.playersList.GetCount() > 0:
            self.playersList.SetSelection(self.playersList.GetCount() - 1)
            self.onSelection(0)
        else:
            self.nameTextCtrl.Clear()
            self.saveButton.Disable()
            self.deleteButton.Disable()
            self.droppedCheckBox.SetValue(False)
            self.droppedCheckBox.Disable()
    
    def onDropped(self, event):
        name = self.playersList.GetStringSelection().split(",")[0]
        self.tournament.paivitaPelaaja(name, name, self.droppedCheckBox.GetValue())
    
    def onRoundEntered(self, event):
        self.tournament.max_kierrokset = self.roundCtrl.GetValue()
    
    def onSelection(self, event):
        name = self.playersList.GetStringSelection().split(",")[0]
        self.nameTextCtrl.SetValue(name)
        #sama kuin onDelete:ssä
        player = self.tournament.pelaajat[name]
        self.droppedCheckBox.SetValue(player.dropped)
        self.saveButton.Enable()
        if not self.started:
            self.deleteButton.Enable()
        if player.round_dropped != -1 and player.round_dropped != self.tournament.kierros:
            self.droppedCheckBox.Disable()
        else:
            self.droppedCheckBox.Enable()
    
    def hasStarted(self):
        self.deleteButton.Disable()
        self.addButton.Disable()
        self.started = True
        self.draftCheckBox.Disable()
        self.eliminationCheckBox.Disable()
        self.seatingsButton.Disable()

        

class Matches(Form):
    def doLayout(self):
        boxSizer = wx.BoxSizer(orient = wx.HORIZONTAL)
        gridSizer = wx.FlexGridSizer(rows = 5, cols = 2, vgap = 10, hgap = 10)
        
        expandOption = dict(flag = wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0,0), noOptions)
        
        for control, options in \
                [(self.pairingsButton, noOptions),
                 (self.endRoundButton, noOptions),
                 (self.winnerLabel, noOptions),
                 (self.winnerComboBox, expandOption),
                 (self.resultRadioBox, dict(flag = wx.ALIGN_CENTER))]:
            gridSizer.Add(control, **options)
            
        for control, options in \
                [(gridSizer, dict(border = 5, flag = wx.ALL)),
                 (self.matchesList, dict(border = 5, flag = wx.ALL | wx.EXPAND,
                    proportion = 1))]:
            boxSizer.Add(control, **options)
        
        self.SetSizerAndFit(boxSizer)
    
    def createControls(self):
        results = ["1-0", "2-0", "2-1", "1-0-1", "1-1", "1-1-1"]
        self.matchesList = wx.ListBox(self, style = wx.LB_SINGLE)
        self.pairingsButton = wx.Button(self, label = "Generate pairings")
        self.endRoundButton = wx.Button(self, label = "End round")
        self.winnerLabel = wx.StaticText(self, label = "Winner:")
        self.winnerComboBox = wx.ComboBox(self, choices = ["", "Player 1", 
            "Player 2", "Draw"], style = wx.CB_READONLY)
        self.resultRadioBox = wx.RadioBox(self, label = "Result", 
            choices = results, majorDimension = 3, style =  wx.RA_SPECIFY_COLS)
        
        font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.matchesList.SetFont(font1)
    
    def bindEvents(self):
        for control, event, handler in \
            [(self.pairingsButton, wx.EVT_BUTTON, self.generatePairings),
             (self.endRoundButton, wx.EVT_BUTTON, self.endRound),
             (self.winnerComboBox, wx.EVT_COMBOBOX, self.selectWinner),
             (self.resultRadioBox, wx.EVT_RADIOBOX, self.selectResult),
             (self.matchesList, wx.EVT_LISTBOX, self.onSelection)]:
            control.Bind(event, handler)
    
    def setTournament(self, tournament_, tournament_form):
        self.tournament = tournament_
        self.otherForm = tournament_form
        self.matchesList.Clear()
        self.pairingsButton.Enable()
        self.endRoundButton.Disable()
        self.winnerComboBox.Disable()
        self.resultRadioBox.Disable()
    
    def generatePairings(self, event):
        dlg = wx.MessageDialog(self, "Generate pairings?", "?",
            pos = self.GetPosition(), style = wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.otherForm.hasStarted()
            self.tournament.parita()
            for m in self.tournament.matsit:
                self.matchesList.Append(m.otsikko())
            self.pairingsButton.Disable()
            self.endRoundButton.Enable()
        dlg.Destroy()
    
    #Kun valitaan matsi, asetetaan tuloksen näyttävä radiobox
    #ja voittajan näyttävä combobox oikeaan asentoon
    def onSelection(self, event):
        matsi = self.tournament.annaMatsi(self.matchesList.GetSelection())
        self.winnerComboBox.SetString(1, matsi.pelaaja1.nimi)
        self.winnerComboBox.SetString(2, matsi.pelaaja2.nimi)
        self.winnerComboBox.Enable()
        results = [(1, 0, 0), (2, 0, 0), (2, 1, 0), (1, 0, 1), (1, 1, 0),
            (1, 1, 1)]
        if self.tournament.single_elimination and self.winnerComboBox.GetCount() == 4:
            self.winnerComboBox.Clear()
            self.winnerComboBox.AppendItems(["", "Player 1", "Player 2"])
        elif not self.tournament.single_elimination and self.winnerComboBox.GetCount() < 4:
            self.winnerComboBox.Clear()
            self.winnerComboBox.AppendItems(["", "Player 1", "Player 2", "Draw"])
        if matsi.pelaaja1.nimi == "**Bye**" or matsi.pelaaja2.nimi == "**Bye**":
            self.winnerComboBox.Disable()
            self.resultRadioBox.Disable()
        elif not matsi.pelattu:
            self.resultRadioBox.Disable()
            self.winnerComboBox.SetSelection(0)
        elif matsi.win1 > matsi.win2:
            self.winnerComboBox.SetSelection(1)
            self.setRadioBox()
            self.resultRadioBox.SetSelection(results.index((matsi.win1, 
                matsi.win2, matsi.draws)))
        elif matsi.win1 == matsi.win2:
            self.winnerComboBox.SetSelection(3)
            self.setRadioBox()
            self.resultRadioBox.SetSelection(results.index((matsi.win1,
                matsi.win2, matsi.draws)))
        else:
            self.winnerComboBox.SetSelection(2)
            self.setRadioBox()
            self.resultRadioBox.SetSelection(results.index((matsi.win2, 
                matsi.win1, matsi.draws)))
            
    
    def endRound(self, event):
        pelattu = self.tournament.kaikkiPelattu()
        if not pelattu:
            dlg = wx.MessageDialog(self, "All results haven't been reported",
                "Error", pos = self.GetPosition(), style = wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, "End round?", "?", pos = self.GetPosition(),
            style = wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.endRoundButton.Disable()
            self.winnerComboBox.Disable()
            self.resultRadioBox.Disable()
            self.matchesList.Clear()
            self.tournament.lopetaKierros()
            if self.tournament.kierros < self.tournament.max_kierrokset:
                self.pairingsButton.Enable()
            self.otherForm.onSelection(1)
        dlg.Destroy()
        
    def selectWinner(self, event):
        self.setRadioBox()
        self.selectResult(event)
    
    #asetetaan radioboxin namiskat päälle tai pois ettei
    #voi valita esim. 2-0 jos on valittu tasuri
    def setRadioBox(self):
        self.resultRadioBox.Enable()
        for n in range(6):
            self.resultRadioBox.EnableItem(n, True)
        if self.winnerComboBox.GetSelection() == 0:
            self.resultRadioBox.Disable()
        if self.winnerComboBox.GetSelection() != 3:
            self.resultRadioBox.EnableItem(4, False)
            self.resultRadioBox.EnableItem(5, False)
            self.resultRadioBox.SetSelection(1)
        else:
            for n in range(4):
                self.resultRadioBox.EnableItem(n, False)
            self.resultRadioBox.SetSelection(4)
    
    def selectResult(self, event):
        results = [(1, 0, 0), (2, 0, 0), (2, 1, 0), (1, 0, 1), (1, 1, 0),
            (1, 1, 1)]
        index = self.matchesList.GetSelection()
        win1 = results[self.resultRadioBox.GetSelection()][0]
        win2 = results[self.resultRadioBox.GetSelection()][1]
        draws = results[self.resultRadioBox.GetSelection()][2]
        if self.winnerComboBox.GetSelection() == 0:
            self.tournament.annaMatsi(index).tulos(0, 0, 0, False)
        elif self.winnerComboBox.GetSelection() == 1:
            self.tournament.annaMatsi(index).tulos(win1, win2, draws, True)
        else:
            self.tournament.annaMatsi(index).tulos(win2, win1, draws, True)
        self.matchesList.SetString(index, self.tournament.annaMatsi(index).otsikko())

class Standings(Form):
    def doLayout(self):
        boxSizer = wx.BoxSizer(orient = wx.HORIZONTAL)

        boxSizer.Add(self.standingsText, **dict(border = 5, flag = wx.ALL | wx.EXPAND,
                    proportion = 1))
        
        self.SetSizerAndFit(boxSizer)
        
        return
    def createControls(self):
        self.standingsText = wx.TextCtrl(self, style = wx.TE_MULTILINE | 
            wx.TE_READONLY)
        font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.standingsText.SetFont(font1)
    def bindEvents(self):
        return
    def setTournament(self, tournament_):
        self.tournament = tournament_
    def updateStandings(self):
        self.standingsText.SetValue(self.tournament.standings())

        
class MainWindow(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        tournament = parittaja.Turnaus("asdf")
        
        self.notebook = wx.Notebook(self)
        self.form1 = Tournament(self.notebook)
        self.form2 = Matches(self.notebook)
        self.form3 = Standings(self.notebook)
        self.notebook.AddPage(self.form1, 'Tournament')
        self.notebook.AddPage(self.form2, 'Matches')
        self.notebook.AddPage(self.form3, 'Standings')
        self.form1.setTournament(tournament, self.form2)
        self.form2.setTournament(tournament, self.form1)
        self.form3.setTournament(tournament)
        self.CreateStatusBar()
        
        filemenu = wx.Menu()
        menuNew = filemenu.Append(wx.ID_NEW, "&New tournament", "Start a new tournament")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", "About this program")
        menuExit = filemenu.Append(wx.ID_EXIT, "&Exit", "Exit program")
        
        
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        self.SetMenuBar(menuBar)
        
        
        self.Bind(wx.EVT_MENU, self.OnNew, menuNew)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.updateStandings)
        
        self.SetClientSize(wx.Size(800, 600))
        
    def updateStandings(self, event):
        if event.GetSelection() == 2:
            self.form3.updateStandings()
        event.Skip()
            
    def OnNew(self, e):
        dlg = wx.MessageDialog(self, "Start new tournament?", "?", 
            pos = self.GetPosition(), style = wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            tournament = parittaja.Turnaus("asdf")
            self.form1.setTournament(tournament, self.form2)
            self.form2.setTournament(tournament, self.form1)
            self.form3.setTournament(tournament)
        dlg.Destroy()
        
    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, "Pairingsien generointisofta v 0.3", "Softasta",
            pos = self.GetScreenPosition(), style = wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnExit(self, e):
        self.Close(True)
        
if __name__ == '__main__':
    app = wx.App(0)
    frame = MainWindow(None, title='MTG-parittaja')
    frame.Show()
    app.MainLoop()