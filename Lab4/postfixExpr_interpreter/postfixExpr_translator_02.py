from lex_my_lang_03 import lex, tableToPrint
from lex_my_lang_03 import tableOfSymb, tableOfId, tableOfConst, tableOfLabel, sourceCode, FSuccess

lex()

# Список для зберігання ПОЛІЗу - 
# коду у постфіксній формі
postfixCode = []

# номер рядка таблиці розбору/лексем/символів ПРОГРАМИ tableOfSymb
numRow = 1
numLineProg = 2
brack = False

# довжина таблиці символів програми
# він же - номер останнього запису
len_tableOfSymb = len(tableOfSymb)
toView = False


def postfixTranslator():
    global len_tableOfSymb, FSuccess
    lex()
    len_tableOfSymb = len(tableOfSymb)
    # чи був успішним лексичний розбір
    if (True, 'Lexer') == FSuccess:
        FSuccess = parseProgram()
        if FSuccess != None:
            serv()
        return FSuccess


# Функція для розбору за правилом
# Program = program StatementList end
# читає таблицю розбору tableOfSymb
def parseProgram():
    global FSuccess
    try:
        # перевірити наявність ключового слова 'program'
        parseToken('program', 'keyword', '')  # Трансляція не потрібна
        # лексема не має операційної семантики

        # перевірити синтаксичну коректність списку інструкцій StatementList
        parseStatementList()  # Трансляція (тут нічого не робити)
        # ця функція сама згенерує
        # та додасть ПОЛІЗ інструкцій (виразів)

        # перевірити наявність ключового слова 'end'
        parseToken('end', 'keyword', '')  # Трансляція не потрібна
        # лексема не має операційної семантики

        # повідомити про успішність
        # синтаксичного аналізу
        # та трансляції програми ПОЛІЗ
        print('Translator: Переклад у ПОЛІЗ та синтаксичний аналіз завершились успішно')
        FSuccess = (True, 'Translator')
        return FSuccess
    except SystemExit as e:
        # Повідомити про виняток
        # Тут всі можливі помилки - синтаксичні
        print('Parser: Аварійне завершення програми з кодом {0}'.format(e))


# Функція перевіряє, чи у поточному рядку таблиці розбору
# зустрілась вказана лексема lexeme з токеном token
# параметр indent - відступ при виведенні у консоль
def parseToken(lexeme, token, indent):
    # доступ до поточного рядка таблиці розбору
    global numRow

    # якщо всі записи таблиці розбору прочитані,
    # а парсер ще не знайшов якусь лексему
    if numRow > len_tableOfSymb:
        failParse('неочікуваний кінець програми', (lexeme, token, numRow))

    # прочитати з таблиці розбору
    # номер рядка програми, лексему та її токен
    numLine, lex, tok = getSymb()

    # тепер поточним буде наступний рядок таблиці розбору
    numRow += 1

    # чи збігаються лексема та токен таблиці розбору з заданими
    if (lex, tok) == (lexeme, token):
        # вивести у консоль номер рядка програми та лексему і токен
        return True
    else:
        # згенерувати помилку та інформацію про те, що
        # лексема та токен таблиці розбору (lex,tok) відрізняються від
        # очікуваних (lexeme,token)
        failParse('невідповідність токенів', (numLine, lex, tok, lexeme, token))
        return False


# Прочитати з таблиці розбору поточний запис
# Повертає номер рядка програми, лексему та її токен
def getSymb():
    if numRow > len_tableOfSymb:
        failParse('getSymb(): неочікуваний кінець програми', numRow)
    # таблиця розбору реалізована у формі словника (dictionary)
    numLine, lexeme, token, _ = tableOfSymb[numRow]
    return numLine, lexeme, token


# Обробити помилки
# вивести поточну інформацію та діагностичне повідомлення
def failParse(str, tuple):
    if str == 'неочікуваний кінець програми':
        (lexeme, token, numRow) = tuple
        print('Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером '
              '{1}. \n\t Очікувалось - {0}'.format((lexeme, token), numRow))
        exit(1001)
    if str == 'getSymb(): неочікуваний кінець програми':
        numRow = tuple
        print('Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером '
              '{0}. \n\t Останній запис - {1}'.format(numRow, tableOfSymb[numRow - 1]))
        exit(1002)
    elif str == 'невідповідність токенів':
        (numLine, lexeme, token, lex, tok) = tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - ({3},{4}).'.format(
            numLine, lexeme, token, lex, tok))
        exit(1)
    elif str == 'невідповідність інструкцій':
        (numLine, lex, tok, expected) = tuple
        print(
            'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine, lex,
                                                                                                           tok,
                                                                                                           expected))
        exit(2)
    elif str == 'невідповідність у Expression.Factor':
        (numLine, lex, tok, expected) = tuple
        print(
            'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine, lex,
                                                                                                           tok,
                                                                                                           expected))
        exit(3)
    elif str == 'Тіло циклу for порожнє.':
        (numLine, lex, tok) = tuple
        print('Parser ERROR: \n\t В рядку {0}. \n\t Тіло циклу for порожнє.'.format(numLine))
        exit(4)


# Функція для розбору за правилом для StatementList
# StatementList = Statement  { Statement }
# викликає функцію parseStatement() доти,
# доки parseStatement() повертає True
def parseStatementList():
    while parseStatement():
        pass
    return True


def parseStatement():
    # прочитаємо поточну лексему в таблиці розбору
    numLine, lex, tok = getSymb()
    # якщо токен - ідентифікатор
    # обробити інструкцію присвоювання
    if tok == 'ident':
        parseAssign()
        return True
    elif (lex, tok) == ('if', 'keyword'):
        parseIf()
        return True
    elif (lex, tok) == ('for', 'keyword'):
        parseFor()
        return True
    elif (lex, tok) == ('while', 'keyword'):
        parseWhile()
        return True
    elif lex == 'input':
        parseInput()
        return True
    elif lex == 'print':
        parsePrint()
        return True

    # тут - ознака того, що всі інструкції були коректно
    # розібрані і була знайдена остання лексема програми.
    # тому parseStatement() має завершити роботу
    elif (lex, tok) == ('end', 'keyword'):
        return False

    else:
        # жодна з інструкцій не відповідає
        # поточній лексемі у таблиці розбору,
        failParse('невідповідність інструкцій', (numLine, lex, tok, 'ident або if'))
        return False


def parsePrint():
    numLine, lex, tok = getSymb()
    global numRow
    print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
    numRow += 1
    parseToken('(', 'brackets_op', '\t' * 7)
    parseExpression()
    postfixCode.append(('print', 'Input'))
    k = True
    while (k):
        k = readWriteMany('print', "Input")
    parseToken(')', 'brackets_op', '\t' * 7)
    return True


def parseInput():
    numLine, lex, tok = getSymb()
    global numRow
    print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
    numRow += 1
    parseToken('(', 'brackets_op', '\t' * 7)
    parseExpression()
    postfixCode.append(('input', 'Print'))
    k = True
    while (k):
        k = readWriteMany('input', "Print")
    parseToken(')', 'brackets_op', '\t' * 7)
    return True


def readWriteMany(lexApp, tokApp):
    numLine, lex, tok = getSymb()
    global numRow
    if (lex == ','):
        numRow += 1
        parseExpression()
        postfixCode.append((lexApp, tokApp))
        return True
    else:
        return False


def parseAssign():
    # номер запису таблиці розбору
    global numRow, postfixCode

    # взяти поточну лексему
    # вже відомо, що це - ідентифікатор
    _numLine, lex, tok = getSymb()

    # починаємо трансляцію інструкції присвоювання за означенням:
    postfixCode.append((lex, tok))  # Трансляція
    # ПОЛІЗ ідентифікатора - ідентифікатор

    if toView: configToPrint(lex, numRow)

    # встановити номер нової поточної лексеми
    numRow += 1

    # якщо була прочитана лексема - ':='
    if parseToken('=', 'assign_op', '\t\t\t\t\t'):
        # розібрати арифметичний вираз
        parseExpression()  # Трансляція (тут нічого не робити)
        # ця функція сама згенерує
        # та додасть ПОЛІЗ виразу

        postfixCode.append(('=', 'assign_op'))  # Трансляція
        # Бінарний оператор  '='
        # додається після своїх операндів
        if toView: configToPrint('=', numRow)
        return True
    else:
        return False


# виводить у консоль інформацію про
# перебіг трансляції
def configToPrint(lex, numRow):
    stage = '\nКрок трансляції\n'
    stage += 'лексема: \'{0}\'\n'
    stage += 'tableOfSymb[{1}] = {2}\n'
    stage += 'postfixCode = {3}\n'
    print(stage.format(lex, numRow, str(tableOfSymb[numRow]), str(postfixCode)))


def parseExpression():
    global numRow, postfixCode
    _numLine, lex, tok = getSymb()
    parseTerm()  # Трансляція (тут нічого не робити)
    # ця функція сама згенерує
    # та додасть ПОЛІЗ доданка
    F = True
    # продовжувати розбирати Доданки (Term)
    # розділені лексемами '+' або '-'
    while F:
        _numLine, lex, tok = getSymb()
        if tok in ('add_op'):
            numRow += 1
            parseTerm()  # Трансляція (тут нічого не робити)
            # ця функція сама згенерує
            # та додасть ПОЛІЗ доданка

            # Трансляція
            postfixCode.append((lex, tok))
            # lex - бінарний оператор  '+' чи '-'
            # додається після своїх операндів
            if toView: configToPrint(lex, numRow)
        else:
            F = False
    return True


def parseTerm():
    global numRow, postfixCode
    parseFactor()  # Трансляція (тут нічого не робити)
    # ця функція сама згенерує
    # та додасть ПОЛІЗ множника
    F = True
    # продовжувати розбирати Множники (Factor)
    # розділені лексемами '*' або '/'
    while F:
        _numLine, lex, tok = getSymb()
        if tok in ('mult_op'):
            numRow += 1
            parseFactor()  # Трансляція (тут нічого не робити)
            # ця функція сама згенерує та додасть ПОЛІЗ множника

            # Трансляція
            postfixCode.append((lex, tok))
            # lex - бінарний оператор  '*' чи '/'
            # додається після своїх операндів
            if toView: configToPrint(lex, numRow)
        elif tok in ('pow_op'):
            numRow += 1
            parseFactor()  # Трансляція (тут нічого не робити)
            # ця функція сама згенерує та додасть ПОЛІЗ множника

            # Трансляція
            postfixCode.append((lex, tok))
            # lex - бінарний оператор  '*' чи '/'
            # додається після своїх операндів
            if toView: configToPrint(lex, numRow)
        else:
            F = False
    return True


def parseIf():
    global numRow
    _, lex, tok = getSymb()
    if lex == 'if' and tok == 'keyword':
        # 'if' нічого не додає до ПОЛІЗу # Трансляція
        numRow += 1

        parseExpression()
        parseBoolExpr()
        parseToken('then', 'keyword', '\t' * 5)
        # Згенерувати мітку m1 = (lex,'label')
        m1 = createLabel()
        postfixCode.append(m1)  # Трансляція
        postfixCode.append(('JF', 'jf'))

        # додали m1 JF
        parseStatement()  # Трансляція
        k = True
        while (k):
            k = exprMany()
        # Згенерувати мітку m2 = (lex,'label')

        m3 = createLabel()
        postfixCode.append(m3)  # Трансляція
        postfixCode.append(('JMP', 'jump'))

        setValLabel(m1)  # в табл. міток
        postfixCode.append(m1)
        postfixCode.append((':', 'colon'))

        # додали m2 JMP m1 :
        _, symbol, rel_opt = getSymb()
        if symbol == "else":
            parseToken("else", 'keyword', '\t' * 5)
            parseStatement()  # Трансляція
        setValLabel(m3)  # в табл. міток
        postfixCode.append(m3)  # Трансляція
        parseToken("fi", 'keyword', '\t' * 5)
        postfixCode.append((':', 'colon'))
        # додали m2 JMP m1 :
        return True
    else:
        return False


def parseFor():
    global numRow
    numLine, lex, tok = getSymb()
    if lex == 'for' and tok == 'keyword':
        # ----------------------------------------------------
        w1 = createLabel()
        setValLabel(w1)
        postfixCode.append(w1)
        postfixCode.append((':', 'colon'))
        numRow += 1
        parseExpression()
        parseBoolExpr()
        parseToken('by', 'keyword', '\t' * 6)
        w2 = createLabel()
        postfixCode.append(w2)
        postfixCode.append(('JF', 'jf'))

        parseStatement()
        k = True
        while (k):
            k = exprMany()
        postfixCode.append(w1)
        postfixCode.append(('JMP', 'jump'))
        setValLabel(w2)
        postfixCode.append(w2)
        postfixCode.append((':', 'colon'))
        return True
    else:
        return False


def parseWhile():
    global numRow
    numLine, lex, tok = getSymb()
    if lex == 'while' and tok == 'keyword':
        # ----------------------------------------------------
        w1 = createLabel()
        setValLabel(w1)
        postfixCode.append(w1)
        postfixCode.append((':', 'colon'))
        numRow += 1
        parseExpression()
        parseBoolExpr()
        parseToken('do', 'keyword', '\t' * 6)
        w2 = createLabel()
        postfixCode.append(w2)
        postfixCode.append(('JF', 'jf'))

        parseStatement()
        k = True
        while (k):
            k = exprMany()
        postfixCode.append(w1)
        postfixCode.append(('JMP', 'jump'))
        setValLabel(w2)
        postfixCode.append(w2)
        postfixCode.append((':', 'colon'))
        return True
    else:
        return False


def parseBoolExpr():
    global numRow
    global k
    global brack
    numLine, lex, tok = getSymb()
    if lex == 'true' or lex == 'false':
        numRow += 1
        postfixCode.append((lex, tok))  # Трансляція
        return True
    if tok in ('rel_op'):
        numRow += 1
        parseExpression()
        postfixCode.append((lex, tok))
        k = True
        while (k):
            k = andOr()
    else:
        failParse('mismatch in BoolExpr', (numLine, lex, tok, 'rel_op'))
    return True


def andOr():
    numLine, lex, tok = getSymb()
    global numRow
    if lex in ('and', 'or'):
        numRow += 1
        parseExpression()
        parseBoolExpr()
        postfixCode.append((lex, tok))
        return True
    else:
        return False


def exprMany():
    numLine, lex, tok = getSymb()
    global numRow
    if (lex == ','):
        numRow += 1
        parseStatement()
        return True
    else:
        return False


def createLabel():
    global tableOfLabel
    nmb = len(tableOfLabel) + 1
    lexeme = "m" + str(nmb)
    val = tableOfLabel.get(lexeme)
    if val is None:
        tableOfLabel[lexeme] = 'val_undef'
        tok = 'label'  # # #
    else:
        tok = 'Конфлікт міток'
        print(tok)
        exit(1003)
    return (lexeme, tok)


def setValLabel(lbl):
    global tableOfLabel
    lex, _tok = lbl
    tableOfLabel[lex] = len(postfixCode)
    return True


def parseFactor():
    global numRow, postfixCode
    numLine, lex, tok = getSymb()

    # перша і друга альтернативи для Factor
    # якщо лексема - це константа або ідентифікатор
    if tok in ('int', 'real', 'ident'):
        postfixCode.append((lex, tok))  # Трансляція
        # ПОЛІЗ константи або ідентифікатора
        # відповідна константа або ідентифікатор
        if toView: configToPrint(lex, numRow)
        numRow += 1

    # третя альтернатива для Factor
    # якщо лексема - це відкриваюча дужка
    elif lex == '(':
        numRow += 1
        parseExpression()  # Трансляція (тут нічого не робити)
        # ця функція сама згенерує та додасть ПОЛІЗ множника
        # дужки у ПОЛІЗ НЕ додаємо
        parseToken(')', 'brackets_op', '\t' * 7)
    elif lex in ('-'):
        numRow += 1
        numLine, lex, tok = getSymb()
        postfixCode.append((lex, tok))
        if toView: configToPrint(lex, numRow)
        postfixCode.append(('NEG', 'neg_val'))
        numRow += 1
    elif lex in ('+'):
        numRow += 1
        parseExpression()
    else:
        failParse('невідповідність у Expression.Factor',
                  (numLine, lex, tok, 'rel_op, int, real, ident або \'(\' Expression \')\''))
    return True


def serv():
    tableToPrint('Label')
    tableToPrint('Id')
    print('\nПочатковий код програми: \n{0}'.format(sourceCode))
    print('\nКод програми у постфіксній формі (ПОЛІЗ):  \n{0}'.format(postfixCode))
    for lbl in tableOfLabel:
        print('postfixCode[{}:{}]={}'.format(lbl, tableOfLabel[lbl], postfixCode[tableOfLabel[lbl]]))
    return True

# запуск парсера
# postfixTranslator()
