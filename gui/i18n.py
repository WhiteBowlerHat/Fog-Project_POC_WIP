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
        "add_more": "Add more", "add_images": "Images...", "add_folder": "Folder...",
        "dlg_add_images": "Add images", "dlg_add_folder": "Add a folder of images",
        "png_filter": "PNG images (*.png)",
        "manage_sources": "View / remove the input images",
        "sources_title": "Input images",
        "sources_summary": "Sources: {sources}  ·  Images: {images}  ·  Size: {size}  ·  "
                           "Capacity: {capacity}",
        "input_images": "Input images :",
        "capacity_short": "{size} · {n} img",
        "source_sizes": "{size} · capacity {capacity}",
        "capacity_hint": "The images can hold {cap} (1 bit per pixel).",
        "fits_short": "✓ OK",
        "fits": "The message can be sent: it needs {need}, the images can hold {cap}.",
        "missing": "Not enough room: {missing} missing (the message needs {need}, the images "
                   "can hold {cap}). Add more images.",
        "units": "bits|B|KB|MB|GB", "decimal": ".",
        "folder_count": "Folder · {n} images", "single_image": "Image",
        "remove": "Remove", "remove_all": "Remove all",
        "remove_all_question": "Remove all the input images from the list?",
        "no_sources": "No image selected.",
        "missing_images": "Please select at least one input folder or image.",
        "android_output": "On Android, the results are written to this folder of the phone:\n{path}",
        "written_to": "Written to: {path}",
        "conversion": "Image conversion",
        "conversion_hint": "Formats converted to PNG when \"Non-native images\" is on "
                           "(Encrypt panel).",
        "non_native": "Non-native images :",
        "non_native_tip": "On: images in the formats enabled in Settings > Image conversion "
                          "({formats}) can be added. They are converted to PNG during the "
                          "encryption; the original files are not modified.",
        "no_format": "no format enabled",
        "non_native_removed": "These images are not PNG and their format is not converted "
                              "any more: they were removed from the input images.\n\n{list}",
        "images_filter": "Images ({patterns})",
        "reason_format": "format not accepted (enable \"Non-native images\" and the format "
                         "in Settings > Image conversion)",
        "progress_title": "Encryption in progress",
        "stage_load": "Loading the images...",
        "stage_prepare": "Preparing (image order, keys)...",
        "stage_embed": "Hiding the file in the images...",
        "stage_save": "Writing the images...",
        "cancel": "Cancel", "cancelling": "Cancelling...",
        "no_cancel_while_saving": "Writing has started: it can no longer be cancelled.",
        "decrypt_progress_title": "Decryption in progress",
        "stage_read": "Reading the hidden file...",
        "stage_write": "Writing the recovered file...",
        "decrypt_cancelled": "Decryption cancelled. No file was written.",
        "encrypt_cancelled": "Encryption cancelled. No image was written.",
        "images_refused": "These images cannot be used and were not added:\n\n{list}",
        "folder_refused_hint": "A folder that contains an unusable image is not added: add "
                               "its other images one by one.",
        "large_images_warning": "Warning: these images are very large. They were added, but "
                                "the encryption will need a lot of memory (at least {mem}) "
                                "and can be slow:\n\n{list}",
        "large_marker": "⚠ very large",
        "large_tooltip": "Very large image(s): the encryption needs a lot of memory and can "
                         "be slow.",
        "large_line": "{name} : {w} × {h} ({mpx} Mpx)",
        "reason_unreadable": "unreadable, or not a real image",
        "and_more": "... and {n} more",
        "unexpected_error": "Unexpected error:\n{error}",
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
        "missing_encrypt": "Please select the file to hide and the output folder.",
        "missing_decrypt": "Please select the output folder.",
        "images_short": "{n} img · {size}",
        "decrypt_images_hint": "Add exactly the images produced by the encryption (no more, "
                               "no less). Their names and order do not matter.",
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
        "tour.non_native.title": "Non-native images",
        "tour.non_native.text": "On: you can also add <b>JPG, TIFF, BMP or WEBP</b> images. "
                                "They are converted to <b>PNG</b> during the encryption (the "
                                "originals are not modified) and the output images are PNG.<br>"
                                "The converted formats are chosen in <b>Settings &gt; Image "
                                "conversion</b>.",
        "tour.file.title": "File to hide",
        "tour.file.text": "Choose the file to hide. Every type is accepted, no need to zip it. "
                          "Its name and extension are kept.<br>Only the name is shown: the <b>folder</b> "
                          "button on the right shows the full path.",
        "tour.add_more.title": "Input images (image bank)",
        "tour.add_more.text": "<b>Add more</b> adds <b>PNG images</b> or <b>folders</b> of images "
                              "used as cover. They must all be different.<br>The field shows the "
                              "<b>capacity</b> (1 bit per pixel). Once the file to hide is "
                              "chosen, <b>green</b> means the message fits, <b>red</b> shows what "
                              "is missing.<br>The <b>list</b> button shows every source with its "
                              "size and lets you remove some.",
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
        "tour.dec_in.title": "Input images",
        "tour.dec_in.text": "<b>Add more</b> adds the images received: one or more "
                            "<b>folders</b> and / or <b>PNG images</b>. Add <b>only</b> the "
                            "images produced by the encryption, no more, no less; their "
                            "names and order do not matter.<br>The <b>list</b> button shows "
                            "them and lets you remove some.",
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
        "add_more": "Ajouter", "add_images": "Images...", "add_folder": "Dossier...",
        "dlg_add_images": "Ajouter des images", "dlg_add_folder": "Ajouter un dossier d'images",
        "png_filter": "Images PNG (*.png)",
        "manage_sources": "Voir / supprimer les images d'entrée",
        "sources_title": "Images d'entrée",
        "sources_summary": "Sources : {sources}  ·  Images : {images}  ·  Taille : {size}  ·  "
                           "Capacité : {capacity}",
        "input_images": "Images d'entrée :",
        "capacity_short": "{size} · {n} img",
        "source_sizes": "{size} · capacité {capacity}",
        "capacity_hint": "Les images peuvent contenir {cap} (1 bit par pixel).",
        "fits_short": "✓ OK",
        "fits": "Le message peut être transmis : il faut {need}, les images peuvent contenir {cap}.",
        "missing": "Pas assez de place : il manque {missing} (le message demande {need}, les "
                   "images peuvent contenir {cap}). Ajoutez des images.",
        "units": "bits|o|Ko|Mo|Go", "decimal": ",",
        "folder_count": "Dossier · {n} images", "single_image": "Image",
        "remove": "Supprimer", "remove_all": "Tout supprimer",
        "remove_all_question": "Supprimer toutes les images d'entrée de la liste ?",
        "no_sources": "Aucune image sélectionnée.",
        "missing_images": "Veuillez choisir au moins un dossier ou une image d'entrée.",
        "android_output": "Sur Android, les résultats sont écrits dans ce dossier du téléphone :\n{path}",
        "written_to": "Écrit dans : {path}",
        "conversion": "Conversion d'images",
        "conversion_hint": "Formats convertis en PNG quand « Ajout d'images non-natives » est "
                           "activé (partie Chiffrer).",
        "non_native": "Ajout d'images non-natives :",
        "non_native_tip": "Activé : les images aux formats cochés dans Paramètres > Conversion "
                          "d'images ({formats}) peuvent être ajoutées. Elles sont converties en "
                          "PNG pendant le chiffrement ; les fichiers d'origine ne sont pas "
                          "modifiés.",
        "no_format": "aucun format activé",
        "non_native_removed": "Ces images ne sont pas des PNG et leur format n'est plus "
                              "converti : elles ont été retirées des images d'entrée.\n\n{list}",
        "images_filter": "Images ({patterns})",
        "reason_format": "format non accepté (activez « Ajout d'images non-natives » et le "
                         "format dans Paramètres > Conversion d'images)",
        "progress_title": "Chiffrement en cours",
        "stage_load": "Chargement des images...",
        "stage_prepare": "Préparation (ordre des images, clés)...",
        "stage_embed": "Dissimulation du fichier dans les images...",
        "stage_save": "Écriture des images...",
        "cancel": "Annuler", "cancelling": "Annulation...",
        "no_cancel_while_saving": "L'écriture a commencé : il n'est plus possible d'annuler.",
        "decrypt_progress_title": "Déchiffrement en cours",
        "stage_read": "Lecture du fichier caché...",
        "stage_write": "Écriture du fichier retrouvé...",
        "decrypt_cancelled": "Déchiffrement annulé. Aucun fichier n'a été écrit.",
        "encrypt_cancelled": "Chiffrement annulé. Aucune image n'a été écrite.",
        "images_refused": "Ces images ne peuvent pas être utilisées, elles n'ont pas été "
                          "ajoutées :\n\n{list}",
        "folder_refused_hint": "Un dossier qui contient une image inutilisable n'est pas "
                               "ajouté : ajoutez ses autres images une par une.",
        "large_images_warning": "Attention : ces images sont très grandes. Elles ont été "
                                "ajoutées, mais le chiffrement demandera beaucoup de mémoire "
                                "(au moins {mem}) et peut être lent :\n\n{list}",
        "large_marker": "⚠ très grande",
        "large_tooltip": "Image(s) très grande(s) : le chiffrement demande beaucoup de mémoire "
                         "et peut être lent.",
        "large_line": "{name} : {w} × {h} ({mpx} Mpx)",
        "reason_unreadable": "illisible, ou pas une vraie image",
        "and_more": "... et {n} de plus",
        "unexpected_error": "Erreur inattendue :\n{error}",
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
        "missing_encrypt": "Veuillez choisir le fichier à cacher et le dossier de sortie.",
        "missing_decrypt": "Veuillez choisir le dossier de sortie.",
        "images_short": "{n} img · {size}",
        "decrypt_images_hint": "Ajoutez exactement les images produites par le chiffrement "
                               "(ni plus ni moins). Leurs noms et leur ordre n'ont pas "
                               "d'importance.",
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
        "tour.non_native.title": "Ajout d'images non-natives",
        "tour.non_native.text": "Activé : vous pouvez aussi ajouter des images <b>JPG, TIFF, "
                                "BMP ou WEBP</b>. Elles sont converties en <b>PNG</b> pendant le "
                                "chiffrement (les originaux ne sont pas modifiés) et les images "
                                "produites sont des PNG.<br>Les formats convertis se choisissent "
                                "dans <b>Paramètres &gt; Conversion d'images</b>.",
        "tour.file.title": "Fichier à cacher",
        "tour.file.text": "Choisissez le fichier à cacher. Tous les types sont acceptés, inutile "
                          "de le zipper. Son nom et son extension sont conservés.<br>Seul le nom est "
                          "affiché : le bouton <b>dossier</b> à droite montre le chemin "
                          "complet.",
        "tour.add_more.title": "Images d'entrée (banque d'images)",
        "tour.add_more.text": "<b>Ajouter</b> ajoute des <b>images PNG</b> ou des <b>dossiers</b> "
                              "d'images qui servent de couverture. Elles doivent toutes être "
                              "différentes.<br>Le champ indique la <b>capacité</b> (1 bit par "
                              "pixel). Une fois le fichier à cacher choisi, le <b>vert</b> "
                              "confirme que le message tient, le <b>rouge</b> indique ce qui "
                              "manque.<br>Le bouton <b>liste</b> affiche chaque source avec sa "
                              "taille et permet d'en supprimer.",
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
        "tour.dec_in.title": "Images d'entrée",
        "tour.dec_in.text": "<b>Ajouter</b> ajoute les images reçues : un ou plusieurs "
                            "<b>dossiers</b> et / ou des <b>images PNG</b>. Ajoutez "
                            "<b>uniquement</b> les images produites par le chiffrement, ni "
                            "plus ni moins ; leurs noms et leur ordre n'ont pas "
                            "d'importance.<br>Le bouton <b>liste</b> les affiche et permet "
                            "d'en supprimer.",
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


def format_size(bits: int) -> str:
    """Size in the most readable unit: bits, then bytes, KB, MB, GB (1 KB = 1024 B)."""
    units = tr("units").split("|")
    if bits < 8:
        return f"{bits} {units[0]}"
    value, unit = bits / 8, 1
    while value >= 1024 and unit < len(units) - 1:
        value, unit = value / 1024, unit + 1
    text = f"{value:.0f}" if unit == 1 or value >= 100 else f"{value:.1f}".removesuffix(".0")
    return f"{text.replace('.', tr('decimal'))} {units[unit]}"
