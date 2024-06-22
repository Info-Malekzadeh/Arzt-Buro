from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import ttkbootstrap as tb

# SQLAlchemy-Setup definieren
class Setting:
    def getConctStr(self):
        with open("./conect.txt") as f:
            return f.read().strip()

conn = Setting().getConctStr()
engine = create_engine(conn)
Base = declarative_base()

# SQLAlchemy-Modelle definieren
class Personal(Base):
    __tablename__ = "personal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    nachname = Column(String(255))
    ausweisnummer = Column(String(255), unique=True)
    alter = Column(Integer)
    letzter_besuch = Column(Date)
    besuchsberichte = relationship("Besuchsbericht", backref="patient")

    def __init__(self, name="", nachname="", ausweisnummer="", alter=0, letzter_besuch=None):
        self.name = name
        self.nachname = nachname
        self.ausweisnummer = ausweisnummer
        self.alter = alter
        self.letzter_besuch = letzter_besuch

class Besuchsbericht(Base):
    __tablename__ = "besuchsberichte"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('personal.id'))
    besuchsdatum = Column(Date, default=datetime.today().date())
    beschreibung = Column(String)

# Tabellen in der Datenbank erstellen
Base.metadata.create_all(engine)

# Sitzung erstellen
Session = sessionmaker(bind=engine)
session = Session()

# Repository-Klasse für Datenbankoperationen
class Repository:
    def Hinzufuegen(self, obj):
        session.add(obj)
        session.commit()

    def Suchen(self, obj, ausweisnummer):
        return session.query(obj).filter_by(ausweisnummer=ausweisnummer).first()

    def Aktualisieren(self, obj):
        session.commit()

    def Loeschen(self, obj):
        session.delete(obj)
        session.commit()

    def NachIdLesen(self, obj, id):
        return session.query(obj).filter_by(id=id).first()

    def AlleLesen(self, obj):
        return session.query(obj).all()

# Geschäftslogik-Klasse
class blPerson:
    def person_hinzufuegen(self, name, nachname, ausweisnummer, alter):
        person = Repository().Suchen(Personal, ausweisnummer)
        if person is None:
            neue_person = Personal(name=name, nachname=nachname, ausweisnummer=ausweisnummer, alter=alter)
            Repository().Hinzufuegen(neue_person)
            return True
        return False

    def person_suchen(self, ausweisnummer):
        return Repository().Suchen(Personal, ausweisnummer)

    def person_aktualisieren(self, name, nachname, ausweisnummer, alter):
        person = self.person_suchen(ausweisnummer)
        if person:
            person.name = name
            person.nachname = nachname
            person.alter = alter
            Repository().Aktualisieren(person)
            return True
        return False

    def person_loeschen(self, ausweisnummer):
        person = self.person_suchen(ausweisnummer)
        if person:
            Repository().Loeschen(person)
            return True
        return False

    def besuchsbericht_hinzufuegen(self, ausweisnummer, besuchsdatum, beschreibung):
        person = self.person_suchen(ausweisnummer)
        if person:
            neuer_bericht = Besuchsbericht(patient_id=person.id, besuchsdatum=besuchsdatum, beschreibung=beschreibung)
            Repository().Hinzufuegen(neuer_bericht)
            return True
        return False

    def besuche_nach_datum_abrufen(self, besuchsdatum):
        return session.query(Besuchsbericht).filter_by(besuchsdatum=besuchsdatum).all()

# GUI-Anwendungsklasse
class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Patientenverwaltung")
        self.master.geometry("1150x450")
        self.master.resizable(False, False)
        

        # Stil-Konfiguration
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TEntry", font=("Helvetica", 12))

        # Hauptframe erstellen
        main_frame = ttk.Frame(master)
        main_frame.pack(fill=BOTH, expand=True)

        # Drei Spalten erstellen
        self.spalte1 = ttk.Frame(main_frame)
        self.spalte1.grid(row=0, column=0, padx=10, pady=10, sticky=(N, W, E, S))

        self.spalte2 = ttk.Frame(main_frame)
        self.spalte2.grid(row=0, column=1, padx=10, pady=10, sticky=(N, W, E, S))

        self.spalte3 = ttk.Frame(main_frame)
        self.spalte3.grid(row=0, column=2, padx=10, pady=10, sticky=(N, W, E, S))

        # Spalte 1: Neuen Patienten hinzufügen
        self.neuer_patient_frame()

        # Spalte 2: Patientensuche und Besuchsbericht
        self.patientensuche_frame()

        # Spalte 3: Liste der besuchten Patienten
        self.besuchte_patienten_frame()
        
    def clear_fields(self):
        self.txtName.delete(0, END)
        self.txtNachname.delete(0, END)
        self.txtAusweisnummer.delete(0, END)
        self.txtAlter.delete(0, END)
    def focus_name_entry(self):
        self.txtName.focus_set()


    def neuer_patient_frame(self):
        frame = ttk.LabelFrame(self.spalte1, text="Neuen Patienten hinzufügen", padding=10)
        frame.pack(fill=BOTH, expand=True)

        ttk.Label(frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=E)
        self.txtName = ttk.Entry(frame)
        self.txtName.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        self.txtName.insert(0, "Vorname eingeben")

        ttk.Label(frame, text="Nachname:").grid(row=1, column=0, padx=5, pady=5, sticky=E)
        self.txtNachname = ttk.Entry(frame)
        self.txtNachname.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        self.txtNachname.insert(0, "Nachname eingeben")

        ttk.Label(frame, text="Ausweisnummer:").grid(row=2, column=0, padx=5, pady=5, sticky=E)
        self.txtAusweisnummer = ttk.Entry(frame)
        self.txtAusweisnummer.grid(row=2, column=1, padx=5, pady=5, sticky=W)
        self.txtAusweisnummer.insert(0, "Ausweisnummer eingeben")

        ttk.Label(frame, text="Alter:").grid(row=3, column=0, padx=5, pady=5, sticky=E)
        self.txtAlter = ttk.Entry(frame)
        self.txtAlter.grid(row=3, column=1, padx=5, pady=5, sticky=W)
        self.txtAlter.insert(0, "Alter eingeben")

        ttk.Button(frame, text="Hinzufügen",bootstyle="info" , command=self.person_hinzufuegen).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Bearbeitung speichern", command=self.person_bearbeitung_speichern, bootstyle="warning").grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Löschen", command=self.person_loeschen, bootstyle="danger").grid(row=6, column=0, columnspan=2, pady=10)

    def patientensuche_frame(self):
        frame = ttk.LabelFrame(self.spalte2, text="Patientensuche und Besuchsbericht", padding=10)
        frame.pack(fill=BOTH, expand=True)

        ttk.Label(frame, text="Ausweisnummer:").grid(row=0, column=0, padx=5, pady=5, sticky=E)
        self.txtSucheAusweisnummer = ttk.Entry(frame)
        self.txtSucheAusweisnummer.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        self.txtSucheAusweisnummer.insert(0, "Ausweisnummer eingeben")

        ttk.Button(frame, text="Suchen", command=self.person_suchen, bootstyle="success").grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="Besuchsdatum:").grid(row=2, column=0, padx=5, pady=5, sticky=E)
        self.txtBesuchsdatum = ttk.Entry(frame)
        self.txtBesuchsdatum.grid(row=2, column=1, padx=5, pady=5, sticky=W)
        self.txtBesuchsdatum.insert(0, "YYYY-MM-DD")

        ttk.Label(frame, text="Beschreibung:").grid(row=3, column=0, padx=5, pady=5, sticky=E)
        self.txtBeschreibung = ScrolledText(frame, width=40, height=10)
        self.txtBeschreibung.grid(row=3, column=1, padx=5, pady=5, sticky=W)

        ttk.Button(frame, text="Besuchsbericht speichern", command=self.besuchsbericht_speichern, bootstyle="success").grid(row=4, column=0, columnspan=2, pady=10)

    def besuchte_patienten_frame(self):
        frame = ttk.LabelFrame(self.spalte3, text="Besuchte Patienten", padding=10)
        frame.pack(fill=BOTH, expand=True)

        self.lstBesuchtePatenten = Listbox(frame, width=50, height=20)
        self.lstBesuchtePatenten.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        ttk.Button(frame, text="Berichte laden", command=self.berichte_laden, bootstyle="info").grid(row=1, column=0, columnspan=2, pady=10)

    def person_hinzufuegen(self):
        name = self.txtName.get()
        nachname = self.txtNachname.get()
        ausweisnummer = self.txtAusweisnummer.get()
        alter = int(self.txtAlter.get())

        if blPerson().person_hinzufuegen(name, nachname, ausweisnummer, alter):
            messagebox.showinfo("Erfolg", "Patient erfolgreich hinzugefügt.")
            self.clear_fields()
            self.focus_name_entry()
        else:
            messagebox.showerror("Fehler", "Patient mit dieser Ausweisnummer existiert bereits.")

    def person_suchen(self):
        ausweisnummer = self.txtSucheAusweisnummer.get()
        person = blPerson().person_suchen(ausweisnummer)
        if person:
            self.txtName.delete(0, END)
            self.txtNachname.delete(0, END)
            self.txtAusweisnummer.delete(0, END)
            self.txtAlter.delete(0, END)
            self.txtName.insert(0, person.name)
            self.txtNachname.insert(0, person.nachname)
            self.txtAusweisnummer.insert(0, person.ausweisnummer)
            self.txtAlter.insert(0, person.alter)
        else:
            messagebox.showerror("Fehler", "Patient nicht gefunden.")

    def person_bearbeiten(self):
        self.person_suchen()

    def person_bearbeitung_speichern(self):
        name = self.txtName.get()
        nachname = self.txtNachname.get()
        ausweisnummer = self.txtAusweisnummer.get()
        alter = int(self.txtAlter.get())

        if blPerson().person_aktualisieren(name, nachname, ausweisnummer, alter):
            messagebox.showinfo("Erfolg", "Patientendaten erfolgreich aktualisiert.")
            self.clear_fields()
            self.focus_name_entry()
        else:
            messagebox.showerror("Fehler", "Aktualisierung fehlgeschlagen.")

    def person_loeschen(self):
        ausweisnummer = self.txtAusweisnummer.get()

        if blPerson().person_loeschen(ausweisnummer):
            messagebox.showinfo("Erfolg", "Patient erfolgreich gelöscht.")
            self.clear_fields()
            self.focus_name_entry()
        else:
            messagebox.showerror("Fehler", "Löschung fehlgeschlagen.")
    def besuchsbericht_speichern(self):
        ausweisnummer = self.txtSucheAusweisnummer.get()
        besuchsdatum = self.txtBesuchsdatum.get()
        beschreibung = self.txtBeschreibung.get("1.0", END).strip()

        try:
            besuchsdatum = datetime.strptime(besuchsdatum, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Fehler", "Falsches Datumformat. Bitte YYYY-MM-DD verwenden.")
            return

        if blPerson().besuchsbericht_hinzufuegen(ausweisnummer, besuchsdatum, beschreibung):
            messagebox.showinfo("Erfolg", "Besuchsbericht erfolgreich gespeichert.")
        else:
            messagebox.showerror("Fehler", "Fehler beim Speichern des Besuchsberichts.")

    def berichte_laden(self):
        self.lstBesuchtePatenten.delete(0, END)
        berichte = blPerson().besuche_nach_datum_abrufen(datetime.today().date())

        for bericht in berichte:
            patient = Repository().NachIdLesen(Personal, bericht.patient_id)
            if patient:
                self.lstBesuchtePatenten.insert(END, f"{patient.name} {patient.nachname} ({patient.ausweisnummer}): {bericht.beschreibung}")

if __name__ == "__main__":
    root = tb.Window(themename="flatly")
    app = App(root)
    root.mainloop()
