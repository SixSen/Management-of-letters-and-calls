# encoding=utf-8
import xlrd
import jieba
import jieba.posseg as pseg
# 读取excel
def read_excel(file):
    wb = xlrd.open_workbook(file)
    ws = wb.sheet_by_name('sheet1')
    dataset = []
    for r in range(ws.nrows):
        col = []
        for c in range(ws.ncols):
            col.append(ws.cell(r, c).value)
        dataset.append(col)
    dataword = []
    for n in range(ws.nrows):
        if n != 0:
            dataword.append(dataset[n][2])
            dataword[n - 1].encode('utf-8')
    return dataword

# 分词
def spilt_word(data):
    seg_list=[]
    for n in data:
        seg_list.append(list(jieba.cut(n)))
    return seg_list

# 关系关键词关联判定(一封信，一组关键词)
def relation_word_count(seg, kwoc):
    count = 0
    evidence = ""
    evidences = []
    distance = 0
    kwoc_temp = kwoc[:]
    tillend_flag = 0
    for n in seg:                                 #词语
        evidence = evidence + n                   #词语合并为句子成证据
        if(n == "。" ):                           #句号重新初始化
            if (tillend_flag == 1):
                evidences.append(evidence)
                tillend_flag = 0
            evidence = ""
            kwoc_temp = kwoc[:]
        elif(tillend_flag == 1):                  #继续往后找句号
            continue
        else:
            kwoc_index = 0                        #关键词下标初始化
            for kw in kwoc_temp:
                if len(kw) == 1:
                    for cw in kw[0]:
                        if(cw in n):

                            distance = 0
                            del kwoc_temp[kwoc_index]
                            kwoc_index = 0
                            break
                elif(kw in n):

                    distance = 0
                    del kwoc_temp[kwoc_index]  # 删去检索到关键词，初始化下标
                    kwoc_index = 0
                if (len(kwoc_temp) == 0):
                    count += 1
                    tillend_flag = 1
                kwoc_index += 1
        distance += 1
        if(distance > 5):                         #距离超过5则重置
            kwoc_temp = kwoc[:]
            distance = 0
    if(evidence != '' and tillend_flag == 1):
        evidences.append(evidence)
    if count != 0:
        return [count, evidences]

# 结果判定
def result_judegement(results):
    index = 0
    max = None
    for result in results:
        if result:
            if max == None:
                max = result
            elif max[0] > result[0]:
                max = result
    return max

# 识别地名
def get_acc_area(data):
    jieba.load_userdict("text/add_words.txt")
    word_tag = pseg.cut(data)
    areas = []
    for word,tag in word_tag:
        flag = 1
        if(tag == 'ns'):
            areas_index = 0
            for area,count in areas:

                if area == word:
                    areas[areas_index][1]+=1
                    flag = 0
            if flag == 1:
                areas.append([word,1])
            areas_index+=1
    frequency = 0
    true_area = "未检测到地区"
    for area,count in areas:
        if count > frequency:
            frequency = count
            true_area = area
    return  areas

# 识别人名
def get_acc_name(data):
    jieba.load_userdict("text/add_words.txt")
    word_tag = pseg.cut(data)
    names = []
    for word, tag in word_tag:
        flag = 1
        if (tag == 'nr'):
            areas_index = 0
            for name, count in names:
                if name == word:
                    names[areas_index][1] += 1
                    flag = 0
            if flag == 1:
                names.append([word, 1])
            areas_index += 1
    frequency = 0
    true_name = "未检测到地区"
    for name, count in names:
        if count > frequency:
            frequency = count
            true_name = name
    return names

# 根据ID获取标签名字
def label_int_to_str(label_id):
    label_id_name = {1:'不正当性关系',
                 2:'贪污贿赂行为',
                 3: '侵害群众利益',
                 4: '挪用公款',
                 5: '其他违法犯罪行为',
                 6: '违反工作纪律',
                 7: '违规参与公款宴请消费',
                 8: '违规配备使用公务用车',
                 9: '违法考试录取工作规定',
                 10: '违反干部选拔任用规定',
                 11: '权权交易和以权谋私',
                 12: '损害党和政府的形象',
                 13: '违反廉洁纪律',
                 14: '违规操办婚丧喜庆事宜',
                 15: '违规从事营利活动',
                 16: '违规接受礼品礼金宴请服务',
                 17: '违规发放津贴奖金',
                 18: '在投票和选举中搞非组织活动',
                 19: '未分类',

    }
    name = label_id_name.get(label_id,None)
    return name