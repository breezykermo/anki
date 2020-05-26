import subprocess as sp
import genanki
import re
from pathlib import Path
from DictionaryServices import *
from fastscript import call_parse, Param

WORDS_NAME_ON_REMARKABLE = "ita"
DECK = genanki.Deck(
    2059400110,
    'Elantris'
)
MODEL = genanki.Model(
    1607392319,
    'Main',
    fields=[
        { 'name': 'word' },
        { 'name': 'def' }
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{word}}',
            'afmt': '{{word}}<br><span class="back">{{def}}</span><br><a href="https://translate.google.com/#view=home&op=translate&sl=it&tl=en&text={{word}}">Translate</a>'
        }
    ]
)

# 7-bit C1 ANSI sequences
ANSI_ESCAPE = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)


def trans_remote(wrd, langs="it:en"):
    """ requires https://www.soimort.org/translate-shell/ on path """
    p1 = sp.Popen(["trans", langs, wrd], stdout=sp.PIPE)
    p2 = sp.Popen(["tail", "-n", "4"], stdin=p1.stdout, stdout=sp.PIPE)
    output, err = p2.communicate()
    t = output.decode('utf-8').splitlines()
    t = [wrd.strip() for wrd in ANSI_ESCAPE.sub('', t[3]).strip().split(",")]
    if len(t) == 4:
        return ','.join(t)
    elif len(t) == 3:
        return ANSI_ESCAPE.sub('', t[2]).strip()
    else:
        return None

def get_def(wrd):
    """ Translate locally using Apple dictionary. Must be set to Italian. """
    wrdrange = (0, len(wrd))
    t = DCSCopyTextDefinition(None, wrd, wrdrange)
    if t is None:
        return t
    t = ANSI_ESCAPE.sub('', t)
    t = t.split(' ', 1)[1] # remove repeat of word
    t = t.split(' ETIMOLOGIA ', 1)[0] # remove etimologia
    return t


def remt_export():
    p = sp.Popen(["remt", "export", WORDS_NAME_ON_REMARKABLE, "latest_words.pdf"], stdout=sp.PIPE)
    output, err = p.communicate()
    if not err:
        return True
    return False

def txt_from_words(lines, outfp="out.txt"):
    """ Generate 'out.txt' from a list of words. Word and meaning separated by semicolon. """
    idx = 0
    non_trans = []
    with open(outfp, 'w') as f:
        while idx < len(lines):
            line = lines[idx]
            t_line = get_def(line)
            if t_line is not None:
                t_line = t_line.replace(';', ', ') # replace semicolons
                l = f"{line}; {t_line}\n"
                f.write(l)
                print(l)
            else:
                non_trans.append(line)
            idx += 1


def anki_from_words(lines, output):
    for line in lines:
        definition = get_def(line)
        if definition is None:
            continue
        note = genanki.Note(
            model=MODEL,
            fields=[line, definition]
        )
        DECK.add_note(note)
    genanki.Package(DECK).write_to_file(output)

@call_parse
def main(txt_file: Param("Text file", str),
         output: Param("Output file", str)="output.apkg"):
    wrds = Path(txt_file).read_text().split('\n')
    anki_from_words(wrds, out_file)

