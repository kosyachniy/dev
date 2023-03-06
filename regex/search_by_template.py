import re


TEXT = """
<select id="languageSelect" class="bg-gray-100 border-0 text-sm rounded block w-full dark:bg-gray-600 dark:border-gray-600 dark:hover:bg-gray-900 dark:placeholder-gray-400 dark:text-white hover:bg-gray-200 focus:ring-0">
    <option value="">Default language</option>


    <option value="German">
        Deutsch
        </option>

    <option value="English*">
        English
        </option>

    <option value="Spanish">
        Español
        </option>

    <option value="French">
        Français
        </option>

    <option value="Italian">
        Italiano
        </option>

    <option value="Portuguese">
        Português
        </option>

    <option value="Polish">
        Polski
        </option>

    <option value="Ukrainian">
        Українська
        </option>

    <option value="English">
        ---------------
        </option>

    <option value="Somali">
        Af Soomaali
        </option>

    <option value="Afrikaans">
        Afrikaans
        </option>

    <option value="Azerbaijani">
        Azərbaycan dili
        </option>

    <option value="Indonesian">
        Bahasa Indonesia
        </option>

    <option value="Malaysian Malay">
        Bahasa Malaysia
        </option>

    <option value="Malay">
        Bahasa Melayu
        </option>

    <option value="Javanese">
        Basa Jawa
        </option>

    <option value="Sundanese">
        Basa Sunda
        </option>

    <option value="Bosnian">
        Bosanski jezik
        </option>

    <option value="Catalan">
        Català
        </option>

    <option value="Czech">
        Čeština
        </option>

    <option value="Chichewa">
        Chichewa
        </option>

    <option value="Welsh">
        Cymraeg
        </option>

    <option value="Danish">
        Dansk
        </option>

    <option value="German">
        Deutsch
        </option>

    <option value="Estonian">
        Eesti keel
        </option>

    <option value="English">
        English
        </option>

    <option value="English (UK)">
        English (UK)
        </option>

    <option value="English (US)">
        English (US)
        </option>

    <option value="Spanish">
        Español
        </option>

    <option value="Esperanto">
        Esperanto
        </option>

    <option value="Basque">
        Euskara
        </option>

    <option value="French">
        Français
        </option>

    <option value="Irish">
        Gaeilge
        </option>

    <option value="Galician">
        Galego
        </option>

    <option value="Croatian">
        Hrvatski jezik
        </option>

    <option value="Xhosa">
        isiXhosa
        </option>

    <option value="Zulu">
        isiZulu
        </option>

    <option value="Icelandic">
        Íslenska
        </option>

    <option value="Italian">
        Italiano
        </option>

    <option value="Swahili">
        Kiswahili
        </option>

    <option value="Haitian Creole">
        Kreyòl Ayisyen
        </option>

    <option value="Kurdish">
        Kurdî
        </option>

    <option value="Latin">
        Latīna
        </option>

    <option value="Latvian">
        Latviešu valoda
        </option>

    <option value="Luxembourgish">
        Lëtzebuergesch
        </option>

    <option value="Lithuanian">
        Lietuvių kalba
        </option>

    <option value="Hungarian">
        Magyar
        </option>

    <option value="Malagasy">
        Malagasy
        </option>

    <option value="Maltese">
        Malti
        </option>

    <option value="Maori">
        Māori
        </option>

    <option value="Dutch">
        Nederlands
        </option>

    <option value="Norwegian">
        Norsk
        </option>

    <option value="Uzbek">
        O'zbek tili
        </option>

    <option value="Polish">
        Polski
        </option>

    <option value="Portuguese">
        Português
        </option>

    <option value="Romanian">
        Română
        </option>

    <option value="Sesotho">
        Sesotho
        </option>

    <option value="Albanian">
        Shqip
        </option>

    <option value="Slovak">
        Slovenčina
        </option>

    <option value="Slovenian">
        Slovenščina
        </option>

    <option value="Finnish">
        Suomi
        </option>

    <option value="Swedish">
        Svenska
        </option>

    <option value="Tagalog">
        Tagalog
        </option>

    <option value="Tatar">
        Tatarça
        </option>

    <option value="Turkish">
        Türkçe
        </option>

    <option value="Vietnamese">
        Việt ngữ
        </option>

    <option value="Yoruba">
        Yorùbá
        </option>

    <option value="Greek">
        Ελληνικά
        </option>

    <option value="Belarusian">
        Беларуская мова
        </option>

    <option value="Bulgarian">
        Български език
        </option>

    <option value="Kyrgyz">
        Кыр
        </option>

    <option value="Kazakh">
        Қазақ тілі
        </option>

    <option value="Macedonian">
        Македонски јазик
        </option>

    <option value="Mongolian">
        Монгол хэл
        </option>

    <option value="Russian" selected="">
        Русский
        </option>

    <option value="Serbian">
        Српски језик
        </option>

    <option value="Tajik">
        Тоҷикӣ
        </option>

    <option value="Ukrainian">
        Українська
        </option>

    <option value="Georgian">
        ქართული
        </option>

    <option value="Armenian">
        Հայերեն
        </option>

    <option value="Yiddish">
        ייִדיש
        </option>

    <option value="Hebrew">
        עברית
        </option>

    <option value="Uyghur">
        ئۇيغۇرچە
        </option>

    <option value="Urdu">
        اردو
        </option>

    <option value="Arabic">
        العربية
        </option>

    <option value="Pashto">
        پښتو
        </option>

    <option value="Persian">
        فارسی
        </option>

    <option value="Nepali">
        नेपाली
        </option>

    <option value="Marathi">
        मराठी
        </option>

    <option value="Hindi">
        हिन्दी
        </option>

    <option value="Bengali">
        বাংলা
        </option>

    <option value="Punjabi">
        ਪੰਜਾਬੀ
        </option>

    <option value="Gujarati">
        ગુજરાતી
        </option>

    <option value="Oriya">
        ଓଡ଼ିଆ
        </option>

    <option value="Tamil">
        தமிழ்
        </option>

    <option value="Telugu">
        తెలుగు
        </option>

    <option value="Kannada">
        ಕನ್ನಡ
        </option>

    <option value="Malayalam">
        മലയാളം
        </option>

    <option value="Sinhala">
        සිංහල
        </option>

    <option value="Thai">
        ไทย
        </option>

    <option value="Lao">
        ພາສາລາວ
        </option>

    <option value="Burmese">
        ဗမာစာ
        </option>

    <option value="Khmer">
        ភាសាខ្មែរ
        </option>

    <option value="Korean">
        한국어
        </option>

    <option value="Chinese">
        中文
        </option>

    <option value="Traditional Chinese">
        繁體中文
        </option>

    <option value="Japanese">
        日本語
        </option>

</select>
"""

for i in re.findall(r'<option value="\W*(\w*)\W*">\W*(\w*)\W*</option>', TEXT):
    print(i)
