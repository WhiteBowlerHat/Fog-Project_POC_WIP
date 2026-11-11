"""Translations of the GUI (English / French).

    tr("key")                 -> text in the current language
    tr("done_nonce", nonce=n) -> with str.format() arguments
    set_language("fr")

The choice is remembered between launches with QSettings.
"""
from PySide6.QtCore import QLocale, QSettings

LANGUAGES = {"fr": "Français", "en": "English"}

STRINGS = {
    "en": {
        # window / banner
        "minimize": "Minimize", "maximize": "Maximize", "restore": "Restore", "close": "Close",
        "settings": "Settings", "help": "Help",
        # encrypt part
        "encrypt_box": "Encrypt", "encrypt_btn": "Encrypt",
        "decrypt_box": "Decrypt", "decrypt_btn": "Decrypt",
        "key": "Key :", "show_key": "Show key", "hide_key": "Hide key",
        "confirm_key": "Confirm key :", "view_path": "View Path",
        "tagline": "A thick fog dispelled by a light wind",
        "nonce_in_picture": "Nonce in the metadata :", "yes_state": "Yes", "no_state": "No",
        "select_file": "Select File", "input_folder": "Input Folder",
        "output_folder": "Output Folder", "none": "None",
        "nonce": "Nonce :", "nonce_placeholder": "<Run the program to get the nonce>",
        "nonce_optional": "optional (read from the images if empty)",
        # file dialogs
        "dlg_file": "File To Hide", "dlg_enc_in": "Encrypt Input Folder",
        "dlg_enc_out": "Encrypt Output Folder", "dlg_dec_in": "Decrypt Input Folder",
        "dlg_dec_out": "Decrypt Output Folder",
        # alerts
        "ok": "OK", "yes": "Yes", "no": "No",
        "enter_key": "Please enter a key.",
        "keys_mismatch": "The two keys do not match.",
        "missing_encrypt": "Please select the file to hide, the input folder and the output folder.",
        "missing_decrypt": "Please select the input folder and the output folder.",
        "done": "Done. Send all the images of the output folder to the receiver, "
                "and give them the key through another channel.",
        "done_nonce": "Done. The nonce is NOT stored in the images. Keep it: without it "
                      "the file cannot be recovered.\n\nNonce : {nonce}\n\n"
                      "Send all the images of the output folder to the receiver, and give "
                      "them the key and the nonce through another channel.",
        "recovered": "Recovered file written to:\n{path}",
        # drawers
        "help_title": "Help", "tutorial": "Tutorial", "about": "About",
        "settings_title": "Settings", "language": "Language",
        "tutorial_question": "Would you like a guided tour of how to use the software?",
        "language_question": "Switch the language to {lang}?",
        "translating": "Translating...",
        "about_text": "<b>Fog Project</b><br><br>"
                      "Hide any file inside a bank of PNG images, at secret positions "
                      "that depend on a key.<br><br>"
                      "<b>Encrypt</b>: choose the file to hide, the bank of PNG images (input "
                      "folder) and an output folder, type a key, then click Encrypt.<br>"
                      "<b>Decrypt</b>: choose the folder of the produced images and an output "
                      "folder, type the same key, then click Decrypt.<br><br>"
                      "Documentation and source code:<br>{link}",
        # tour
        "tour_quit": "Quit", "tour_prev": "Previous", "tour_next": "Next", "tour_finish": "Finish",
        "tour.encrypt.title": "Encrypt (hide a file)",
        "tour.encrypt.text": "This part hides a file of any type (zip, txt, mp4, ...) in a bank "
                             "of PNG images. Follow the fields in order.",
        "tour.key.title": "Key",
        "tour.key.text": "Type a <b>long password</b>. It decides where the bits are hidden "
                         "and it is the only secret: without it, the file cannot be found.<br>"
                         "The <b>eye</b> button shows or hides what you type. Give the key to "
                         "the receiver through another channel than the images.",
        "tour.confirm_key.title": "Confirm key",
        "tour.confirm_key.text": "Type the same key again. It avoids a typo: a key you "
                                 "mistyped once could never be found again.",
        "tour.nonce_switch.title": "Nonce in metadata",
        "tour.nonce_switch.text": "The nonce is a random value (not secret) needed to recover "
                                  "the file.<br><b>Yes</b>: it is stored in the PNG metadata, "
                                  "nothing else to send.<br><b>No</b>: it is shown at the end "
                                  "of the encryption; keep it and send it. Useful when a "
                                  "platform strips metadata (messengers, social networks).",
        "tour.file.title": "File to hide",
        "tour.file.text": "Choose the file to hide. Every type is accepted, no need to zip it. "
                          "Its name and extension are kept.<br>Only the name is shown: the <b>folder</b> "
                          "button on the right shows the full path.",
        "tour.enc_in.title": "Input folder (image bank)",
        "tour.enc_in.text": "The folder of the <b>PNG</b> cover images. They must all be "
                            "different.<br>Capacity: 1 bit per pixel, so you need enough "
                            "images for the size of the file.",
        "tour.enc_out.title": "Output folder",
        "tour.enc_out.text": "The folder where the new images are written. It must differ from "
                             "the bank.<br>Send <b>all</b> the images of this folder, without "
                             "converting or editing them (the PNG must stay intact).",
        "tour.encrypt_btn.title": "Start the encryption",
        "tour.encrypt_btn.text": "When everything is filled in, click <b>Encrypt</b>. A message "
                                 "confirms the end (and shows the nonce if it is not in the "
                                 "images).",
        "tour.decrypt.title": "Decrypt (recover a file)",
        "tour.decrypt.text": "This part recovers the hidden file from the received images.",
        "tour.dec_key.title": "Key",
        "tour.dec_key.text": "Type <b>exactly the same key</b> as the one used to hide the file. "
                             "A wrong key gives an error, never a fake file.",
        "tour.dec_nonce.title": "Nonce (optional)",
        "tour.dec_nonce.text": "Leave it empty if the nonce is in the images (default).<br>"
                               "Otherwise, paste here the nonce shown during the encryption.",
        "tour.dec_in.title": "Input folder",
        "tour.dec_in.text": "The folder containing <b>only</b> the images produced by the "
                            "encryption, no more, no less. Their names and order do not matter.",
        "tour.dec_out.title": "Output folder",
        "tour.dec_out.text": "The folder where the recovered file is written, with its original "
                             "name and extension.",
        "tour.decrypt_btn.title": "Start the decryption",
        "tour.decrypt_btn.text": "Click <b>Decrypt</b>. The path of the recovered file is shown.",
        "tour.help.title": "Help and settings",
        "tour.help.text": "This tour can be started again at any time from <b>Help &gt; "
                          "Tutorial</b>. <b>About</b> gives the link to the GitHub project.<br>"
                          "The language is changed in <b>Settings &gt; Language</b>.",
    },
    "fr": {
        "minimize": "Réduire", "maximize": "Agrandir", "restore": "Restaurer", "close": "Fermer",
        "settings": "Paramètres", "help": "Aide",
        "encrypt_box": "Chiffrer", "encrypt_btn": "Chiffrer",
        "decrypt_box": "Déchiffrer", "decrypt_btn": "Déchiffrer",
        "key": "Clé :", "show_key": "Afficher la clé", "hide_key": "Masquer la clé",
        "confirm_key": "Confirmation de la clé :", "view_path": "Voir chemin",
        "tagline": "Un épais brouillard dissipé par un vent léger",
        "nonce_in_picture": "Nonce dans les métadonnées :", "yes_state": "Oui", "no_state": "Non",
        "select_file": "Fichier à cacher", "input_folder": "Dossier d'entrée",
        "output_folder": "Dossier de sortie", "none": "Aucun",
        "nonce": "Nonce :", "nonce_placeholder": "<Lancez le programme pour obtenir la nonce>",
        "nonce_optional": "facultative (lue dans les images si vide)",
        "dlg_file": "Fichier à cacher", "dlg_enc_in": "Dossier d'entrée (chiffrement)",
        "dlg_enc_out": "Dossier de sortie (chiffrement)",
        "dlg_dec_in": "Dossier d'entrée (déchiffrement)",
        "dlg_dec_out": "Dossier de sortie (déchiffrement)",
        "ok": "OK", "yes": "Oui", "no": "Non",
        "enter_key": "Veuillez saisir une clé.",
        "keys_mismatch": "Les deux clés ne correspondent pas.",
        "missing_encrypt": "Veuillez choisir le fichier à cacher, le dossier d'entrée et le "
                           "dossier de sortie.",
        "missing_decrypt": "Veuillez choisir le dossier d'entrée et le dossier de sortie.",
        "done": "Terminé. Envoyez toutes les images du dossier de sortie au destinataire, "
                "et donnez-lui la clé par un autre canal.",
        "done_nonce": "Terminé. La nonce n'est PAS enregistrée dans les images. Gardez-la : "
                      "sans elle le fichier est irrécupérable.\n\nNonce : {nonce}\n\n"
                      "Envoyez toutes les images du dossier de sortie au destinataire, et "
                      "donnez-lui la clé et la nonce par un autre canal.",
        "recovered": "Fichier retrouvé écrit dans :\n{path}",
        "help_title": "Aide", "tutorial": "Tutoriel", "about": "À propos",
        "settings_title": "Paramètres", "language": "Langue",
        "tutorial_question": "Voulez-vous avoir une visite guidée pour l'usage du logiciel ?",
        "language_question": "Passer la langue en {lang} ?",
        "translating": "Traduction en cours..",
        "about_text": "<b>Fog Project</b><br><br>"
                      "Cache n'importe quel fichier dans une banque d'images PNG, à des "
                      "positions secrètes qui dépendent d'une clé.<br><br>"
                      "<b>Chiffrer</b> : choisissez le fichier à cacher, la banque d'images PNG "
                      "(dossier d'entrée) et un dossier de sortie, tapez une clé, puis cliquez "
                      "sur Chiffrer.<br>"
                      "<b>Déchiffrer</b> : choisissez le dossier des images produites et un "
                      "dossier de sortie, tapez la même clé, puis cliquez sur Déchiffrer.<br><br>"
                      "Documentation et code source :<br>{link}",
        "tour_quit": "Quitter", "tour_prev": "Précédent", "tour_next": "Suivant",
        "tour_finish": "Terminer",
        "tour.encrypt.title": "Chiffrer (cacher un fichier)",
        "tour.encrypt.text": "Cette partie cache un fichier de n'importe quel type (zip, txt, "
                             "mp4, ...) dans une banque d'images PNG. Suivez les champs dans "
                             "l'ordre.",
        "tour.key.title": "Clé",
        "tour.key.text": "Tapez un <b>mot de passe long</b>. Il détermine où sont cachés les "
                         "bits et c'est le seul secret : sans lui, le fichier est introuvable."
                         "<br>Le bouton <b>œil</b> affiche ou masque la saisie. Donnez la clé "
                         "au destinataire par un autre canal que les images.",
        "tour.confirm_key.title": "Confirmation de la clé",
        "tour.confirm_key.text": "Retapez la même clé. Cela évite une faute de frappe : une "
                                 "clé mal saisie ne pourrait jamais être retrouvée.",
        "tour.nonce_switch.title": "Nonce dans les métadonnées",
        "tour.nonce_switch.text": "La nonce est une valeur aléatoire (non secrète) nécessaire "
                                  "pour retrouver le fichier.<br><b>Oui</b> : elle est "
                                  "enregistrée dans les métadonnées des PNG, rien d'autre à "
                                  "transmettre.<br><b>Non</b> : elle est affichée à la fin du "
                                  "chiffrement ; gardez-la et transmettez-la. Utile si une "
                                  "plateforme supprime les métadonnées (messageries, réseaux "
                                  "sociaux).",
        "tour.file.title": "Fichier à cacher",
        "tour.file.text": "Choisissez le fichier à cacher. Tous les types sont acceptés, inutile "
                          "de le zipper. Son nom et son extension sont conservés.<br>Seul le nom est "
                          "affiché : le bouton <b>dossier</b> à droite montre le chemin "
                          "complet.",
        "tour.enc_in.title": "Dossier d'entrée (banque d'images)",
        "tour.enc_in.text": "Le dossier des images <b>PNG</b> qui servent de couverture. Elles "
                            "doivent toutes être différentes.<br>Capacité : 1 bit par pixel, "
                            "donc il faut assez d'images pour la taille du fichier.",
        "tour.enc_out.title": "Dossier de sortie",
        "tour.enc_out.text": "Le dossier où sont écrites les nouvelles images. Il doit être "
                             "différent de la banque.<br>Envoyez <b>toutes</b> les images de ce "
                             "dossier, sans les convertir ni les retoucher (le PNG doit rester "
                             "intact).",
        "tour.encrypt_btn.title": "Lancer le chiffrement",
        "tour.encrypt_btn.text": "Quand tout est rempli, cliquez sur <b>Chiffrer</b>. Un message "
                                 "confirme la fin (et affiche la nonce si elle n'est pas dans "
                                 "les images).",
        "tour.decrypt.title": "Déchiffrer (retrouver un fichier)",
        "tour.decrypt.text": "Cette partie retrouve le fichier caché à partir des images reçues.",
        "tour.dec_key.title": "Clé",
        "tour.dec_key.text": "Tapez <b>exactement la même clé</b> que celle utilisée pour cacher "
                             "le fichier. Une mauvaise clé donne une erreur, jamais un faux "
                             "fichier.",
        "tour.dec_nonce.title": "Nonce (facultative)",
        "tour.dec_nonce.text": "Laissez vide si la nonce est dans les images (cas par défaut)."
                               "<br>Sinon, collez ici la nonce affichée lors du chiffrement.",
        "tour.dec_in.title": "Dossier d'entrée",
        "tour.dec_in.text": "Le dossier contenant <b>uniquement</b> les images produites par le "
                            "chiffrement, ni plus ni moins. Leurs noms et leur ordre n'ont pas "
                            "d'importance.",
        "tour.dec_out.title": "Dossier de sortie",
        "tour.dec_out.text": "Le dossier où sera écrit le fichier retrouvé, avec son nom et son "
                             "extension d'origine.",
        "tour.decrypt_btn.title": "Lancer le déchiffrement",
        "tour.decrypt_btn.text": "Cliquez sur <b>Déchiffrer</b>. Le chemin du fichier retrouvé "
                                 "est affiché.",
        "tour.help.title": "Aide et paramètres",
        "tour.help.text": "Ce tutoriel est accessible à tout moment depuis <b>Aide &gt; "
                          "Tutoriel</b>. <b>À propos</b> donne le lien vers le projet GitHub."
                          "<br>La langue se change dans <b>Paramètres &gt; Langue</b>.",
    },
}

_settings = QSettings("FogProject", "Fog")


def _initial_language():
    saved = _settings.value("language")
    if saved in STRINGS:
        return saved
    return "fr" if QLocale.system().name().startswith("fr") else "en"


_current = _initial_language()


def language() -> str:
    return _current


def set_language(lang: str):
    global _current
    if lang not in STRINGS:
        raise ValueError(f"unknown language {lang!r}")
    _current = lang
    _settings.setValue("language", lang)


def tr(key: str, **kwargs) -> str:
    text = STRINGS[_current].get(key) or STRINGS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text
