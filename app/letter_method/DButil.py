import pymysql
import jieba
import app.letter_method.word_method as wm

db = pymysql.connect("localhost", "root", "1232123", "xinfang")
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 数据库关闭
def close():
    db.close()

# 获得关键词（已进行相近词替换）
# 返回[[问题关键词],[...]]]
def get_keywords_AC(id):

    sql = "SELECT * FROM keyword WHERE label_id = %d" % (id)
    cursor.execute(sql)
    results = cursor.fetchall()
    keywords = []
    for row in results:
        # id = row[0]
        keyword = row[1]
        keywords.append(keyword.split("+"))
    ####
    # print("根据问题找到的关键词组合或关键词************************")
    # print(keywords)
    # print("*****************************************************")
    ####
    for kw in keywords:
        kw_index= 0
        for k in kw:
            if "/" in k:
                bhf_closedword = k.replace('/','')
                closedwords = get_closedWords(bhf_closedword)
                kw[kw_index] = closedwords
            kw_index+=1
    return keywords

# 获得代表词下的相近词
def get_closedWords(behalf_word):

    sql = "SELECT  * FROM closedword WHERE behalf_word ='%s'" % (behalf_word)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        closewords = []
        for row in results:
            closeword = row[1].split("|")
            closewords.append(closeword)
        return closewords
    except:
        return None

# 数据库问题标签数量统计
def get_label_count():

    sql = "SELECT label_id,COUNT(tag_id) FROM xinfang.tag GROUP BY label_id"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# 查询没有判定的信件
def get_no_judgement():

    sql = "select letter_id,contect FROM letter LEFT JOIN (select letter from tag) as t1 " \
          "ON letter_id=letter where t1.letter IS NULL"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# 获得所有关键词
# 返回[[问题标签，[[问题关键词],[...]]]，[...]]
def get_all_keywords():

    sql = "SELECT * FROM keyword "
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        original_label_keywords = []
        for result in results:
            flag = 1
            if len(original_label_keywords) == 0:
                original_label_keywords.append([result[0], [result[1]]])
            else:
                for l_ks in original_label_keywords:
                    if l_ks[0] == result[0]:
                        l_ks[1].append(result[1])
                        flag = 0
                        break
                if flag != 0:
                    original_label_keywords.append([result[0], [result[1]]])
        label_keywords = []
        for l_kws in original_label_keywords:
            l_id = l_kws[0]
            kwoc = []
            for kw in l_kws[1]:
                kw = kw.split("+")
                index = 0
                for k in kw:
                    if "/" in k:
                        bhf_closedword = k.replace('/', '')
                        closedwords = get_closedWords(bhf_closedword)
                        kw[index] = closedwords
                    index += 1
                kwoc.append(kw)
            label_keywords.append([l_id, kwoc])
        return label_keywords
    except Exception as e:
        print(e)
        return None

# 获得所有相近词
def get_all_closedWords():

    sql = "SELECT * FROM closedword "
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        closed_words = []
        for result in results:
            bhf_word = result[0]
            closed_word = result[1].split("|")
            closed_words.append([bhf_word, closed_word])
        return results
    except Exception as e:
        print(e)
        return None

# 获得地区问题占比
def get_area_proportion():

    sql = "SELECT area,COUNT(letter_id) " \
          "FROM (SELECT LEFT(accuseArea,6) as area,letter_id FROM letter) b GROUP BY area"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        area_count = []
        for r in results:
            area = r[0]
            count = r[1]
            area_count.append([area,count])
        return area_count
    except Exception as e:
        print(e)
        return None

# 对信件写入判定
def write_judgement(letter_id,label_id,basis):

    sql = "INSERT INTO tag (letter,label_id,basis) VALUES ( %d,%d,'%s')" % (letter_id,label_id,basis)
    try:
        cursor.execute(sql)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return None

# 写入新的关键词
def write_new_keyword(label_id, keyword):

    pokw = jieba.cut(keyword)
    kw = ""
    for p in pokw:
        if kw == "":
            kw = p
        else:
            kw = kw + "+" + p
    sql = "INSERT INTO keyword VALUES ( %d,'%s')" % (label_id,kw)
    try:
        cursor.execute(sql)
        db.commit()
        print("insert keyword successfully")
        return True
    except Exception as e:
        print(e)
        return None

# 写入新的相近词
def write_new_closedword(behalf_word,closedword):

    sql = "INSERT INTO closedword VALUES ( '%s','%s' ) " % (behalf_word,closedword)
    try:
        cursor.execute(sql)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return None

# 更改信件判定
def update_judegement(letter_id,label_id,new_label_id):

    sql = ("UPDATE tag SET label_id = %d ,basis = ''"
           "WHERE letter = %d AND label_id = %d") % (new_label_id,letter_id,label_id)
    try:
        cursor.execute(sql)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return None

# 更新关键词
def update_keyword(label_id, keyword, new_keyword):

    pokw = jieba.cut(new_keyword)
    nkw = ""
    for p in pokw:
        if nkw == "":
            nkw = p
        else:
            nkw = nkw + "+" + p
    sql = ("UPDATE keyword SET label_id = %d , keyword = '%s' " 
           "WHERE label_id = %d AND keyword = '%s'") % (label_id,nkw,label_id,keyword)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return None

# 更新相近词
def update_closedword(behalf_word, new_closedword):

    sql = ("UPDATE closedword SET behalf_word = '%s' , closedword = '%s' " 
           "WHERE behalf_word = '%s' ") % (behalf_word, new_closedword,behalf_word)
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return None

# 删除关键词
def delete_keyword(label_id,keyword):

    sql = "DELETE FROM keyword WHERE label_id = %d AND keyword = '%s'" % (label_id,keyword)
    try:
        cursor.execute(sql)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return None

# 删除相近词
def delete_closedword(behalf_word):

    sql = "DELETE FROM closedword WHERE behalf_word = '%s' " % (behalf_word)
    try:
        cursor.execute(sql)
        db.commit()
        return True
    except Exception as e:
        print(e)
        return None
