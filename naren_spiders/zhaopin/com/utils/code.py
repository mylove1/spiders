# -*-  coding:utf-8 -*-
# Author  :Guile
# Email  :lavender.lhy@gmail.com
# Date  :15-3-23 下午3:30
# Remarks :


class ErrorCode(object):
    """
    自定义错误编码
    """
    NO_ERROR = 0
    SAVE_FILE_ERROR = 10000
    MAKE_DIR_ERROR = 10001
    RENAME_ERROR = 10002
    SAVE_FILE_SUCCESS = 10003
    MAKE_DIR_SUCCESS = 10004
    RENAME_SUCCESS = 10005
    FILE_PATH_ERROR = 10006
    INSERT_DATA_SUCCESS = 10007
    INSERT_DATA_FAILED = 10008
    INSERT_DATE_ERROR = 10009
    UPDATE_DATA_SUCCESS = 10010
    UPDATE_DATA_FAILED = 10011
    UPDATE_DATA_ERROR = 10012
    DELETE_DATA_SUCCESS = 10013
    DELETE_DATA_FAILED = 10014
    DELETE_DATA_ERROR = 10015
    PROXY_ERROR = 10016
    SEND_MAIL_SUCCESS = 10017
    SEND_MAIL_FAILED = 10018
    SEND_MAIL_ERROR = 10019
    DOWN_LOAD_RESUME_COMPLETE = 20000
    CURRENT_PAGE_NO_RESUME = 20001
    CURRENT_TASK_COMPLETE = 20002
    CURRENT_TASK_ERROR = 20003
    UP_LOAD_RESUME_SUCCESS = 20004
    UP_LOAD_RESUME_FAILED = 20005
    GET_RESUME_ERROR = 20006
    GET_RESUME_UP_TO_MAX = 20007
    GET_RESUME_UP_TO_LIMIT = 20008
    GET_SEARCH_UP_TO_MAX = 20009
    LOGIN_SUCCESS = 20010
    LOGIN_FAILED = 20011
    LOGIN_ERROR = 20012
    GET_SEARCH_PAGE_ERROR = 20013
    SERVICE_DATE_OUT = 20014
    LOGOUT_SUCCESS = 20015
    LOGOUT_FAILED = 20016
    LOGOUT_ERROR = 20017
    GET_RESUME_SUCCESS = 20018
    GET_RESUME_FAILED = 20019
    RESUME_ID_IS_ERROR = 20020
    ACCOUNT_BALANCE_DEFICIENCY = 20021
    RESUME_IS_NOT_LOCAL = 20022
    STORE_RESUME_SUCCESS = 20023
    STORE_RESUME_FAILED = 20024
    RESUME_HAS_CONTACT = 20025
    POST_RESUME_TO_MAX = 20026
    REQUIRED_CONDITION_FAILED = 20027
    GET_TASK_SUCCESS = 30000
    GET_TASK_FAILED = 30001
    GET_TASK_ERROR = 30002
    TASK_ALL_COMPLETE = 30003
    TASK_RESET_SUCCESS = 30004
    TASK_RESET_FAILED = 30005
    TASK_RESET_ERROR = 30006
    NO_TASK_DATA = 30007
    SET_TASK_STATUS_SUCCESS = 30008
    SET_TASK_STATUS_FAILED = 30009
    SET_TASK_STATUS_ERROR = 30010
    MAKE_ACTUAL_TASK_SUCCESS = 30011
    MAKE_ACTUAL_TASK_FAILED = 30012
    MAKE_ACTUAL_TASK_ERROR = 30013
    TASK_REQUESTS_DATA_ERROR = 30014
    MAKE_NORMAL_TASK_SUCCESS = 30015
    MAKE_NORMAL_TASK_FAILED = 30016
    MAKE_NORMAL_TASK_ERROR = 30017
    MAKE_TASK_DATA_SUCCESS = 30018
    MAKE_TASK_DATA_FAILED = 30019
    MAKE_TASK_DATA_ERROR = 30020
    GET_ACCOUNT_SUCCESS = 30021
    GET_ACCOUNT_FAILED = 30022
    GET_ACCOUNT_ERROR = 30023
    MINING_IS_RUNNING = 30024
    MINING_AVAILABLE = 30025
    GET_PROXY_SUCCESS = 30026
    GET_PROXY_FAILED = 30027

    def __init__(self):
        """
        构造函数
        :return:
        """
        super(ErrorCode, self).__init__()

    @staticmethod
    def format(code):
        error_dict = {
            0: "",
            10000: u"保存文件错误",
            10001: u"创建文件夹错误",
            10002: u"文件重命名错误",
            10003: u"保存数据成功",
            10004: u"创建文件夹成功",
            10005: u"文件重命名成功",
            10006: u"文件夹路径错误",
            10007: u"插入数据成功",
            10008: u"插入数据失败",
            10009: u"插入数据错误",
            10010: u"更新数据成功",
            10011: u"更新数据失败",
            10012: u"更新数据错误",
            10013: u"删除数据成功",
            10014: u"删除数据失败",
            10015: u"删除数据错误",
            10016: u"代理错误",
            10017: u"发送email成功",
            10018: u"发送email失败",
            10019: u"发送email错误",
            20000: u"下载简历完成",
            20001: u"当前页没有简历",
            20002: u"当前任务完成",
            20003: u"当前任务出错",
            20004: u"上传简历成功",
            20005: u"上传简历失败",
            20006: u"获取简历错误",
            20007: u"简历查看已达到最大限值",
            20008: u"简历查看次数已达到限定值",
            20009: u"查询超限",
            20010: u"登录成功",
            20011: u"登录失败",
            20012: u"登录错误",
            20013: u"获取搜索页面错误",
            20014: u"服务到期",
            20015: u"退出登录成功",
            20016: u"退出登录失败",
            20017: u"退出登录错误",
            20018: u"获取简历成功",
            20019: u"获取简历失败",
            20020: u"该ID没有简历",
            20021: u"下载简历帐号余额不足",
            20022: u"对不起，您暂时不能下载该份简历，原因是：您选中的简历中存在应聘者所在地超出合同范围的情况。请核实您的情况，若有疑问请与销售或客服人员联系。",
            20023: u"暂存简历成功",
            20024: u"暂存简历失败",
            20025: u"简历已有联系方式",
            20026: u"上传简历达到最大限度",
            20027: u"必要条件不满足",
            30000: u"获得任务成功",
            30001: u"获得任务失败",
            30002: u"获得任务错误",
            30003: u"所有任务都已经完成",
            30004: u"任务重置成功",
            30005: u"任务重置失败",
            30006: u"任务重置错误",
            30007: u"没有任务数据",
            30008: u"设置简历状态成功",
            30009: u"设置简历状态失败",
            30010: u"设置简历状态错误",
            30011: u"生成临时任务成功",
            30012: u"生成临时任务失败",
            30013: u"生成临时任务错误",
            30014: u"临时任务请求数据错误",
            30015: u"生成普通任务成功",
            30016: u"生成普通任务失败",
            30017: u"生成普通任务错误",
            30018: u"生成任务数据成功",
            30019: u"生成任务数据失败",
            30020: u"生成任务数据错误",
            30021: u"获取帐号成功",
            30022: u"获取帐号失败",
            30023: u"获取帐号错误",
            30024: u"挖掘程序正在进行中",
            30025: u"挖掘程序可用",
            30026: u"获取代理成功",
            30027: u"获取代理失败",
            40000: u"参数错误"
        }
        return error_dict.get(code, "未知错误")




class SourceCode(object):
    """
        资源编码
    """
    ZHAO_PIN = 10000
    JOB = 10001
    LIEPIN = 10002



class ParameterCode(object):
    """
        参数编码
    """
    KEY_WORD = "SF_1_1_1"
    CUR_POSITION = "SF_1_1_2"
    CUR_INDUSTRY = "SF_1_1_3"
    WORK_YEARS = "SF_1_1_4"
    DEGREE = "SF_1_1_5"
    CUR_PLACE = "SF_1_1_6"
    UPDATE_TIME = "SF_1_1_7"
    AGE = "SF_1_1_8"
    GENDER = "SF_1_1_9"
    BORN_PLACE = "SF_1_1_10"
    SCHOOL_NAME = "SF_1_1_11"
    SUBJECT_NAME = "SF_1_1_12"
    LANGUAGE_LEVEL = "SF_1_1_13"
    CUR_SALARY = "SF_1_1_14"
    EXP_INDUSTRY = "SF_1_1_16"
    EXP_POSITION = "SF_1_1_17"
    EXP_PLACE = "SF_1_1_18"
    WORK_TYPE = "SF_1_1_19"
    EXP_SALARY = "SF_1_1_20"
    F_WORK_EXPERIENCE = "SF_1_1_21"
    SUBJECT_SKILL = "SF_1_1_22"
    MANAGER_EXPERIENCE = "SF_1_1_23"
    COMPANY_NAME = "SF_1_1_25"
    WORK_STATUS = "SF_1_1_29"
    COMPANY_TYPE = "SF_1_1_31"
    COMPANY_SCALE = "SF_1_1_30"

    JOB_AREA_TEXT = "ctrlSerach$AREA$Text"
    JOB_AREA_VALUE = "ctrlSerach$AREA$Value"
    JOB_TOP_DEGREE_FROM = "ctrlSerach$TopDegreeFrom"
    JOB_TOP_DEGREE_TO = "ctrlSerach$TopDegreeTo"
    JOB_LAST_MODIFY = "ctrlSerach$LASTMODIFYSEL"
    JOB_WORK_YEAR_FROM = "ctrlSerach$WorkYearFrom"
    JOB_WORK_YEAR_TO = "ctrlSerach$WorkYearTo"
    JOB_POSITION_TEXT = "ctrlSerach$WORKFUN1$Text"
    JOB_POSITION_VALUE = "ctrlSerach$WORKFUN1$Value"
    JOB_INDUSTRY_TEXT = "ctrlSerach$WORKINDUSTRY1$Text"
    JOB_INDUSTRY_VALUE = "ctrlSerach$WORKINDUSTRY1$Value"
    JOB_GENDER = "ctrlSerach$SEX"
    JOB_WORK_STATUS = "ctrlSerach$JOBSTATUS"
    JOB_AGE_FROM = "ctrlSerach$AgeFrom"
    JOB_AGE_TO = "ctrlSerach$AgeTo"
    JOB_EXPECT_AREA_TEXT = "ctrlSerach$EXPECTJOBAREA$Text"
    JOB_EXPECT_AREA_VALUE = "ctrlSerach$EXPECTJOBAREA$Value"
    JOB_KEY_WORD = "ctrlSerach$KEYWORD"

    @staticmethod
    def __zhaopin_required__():
        return [ParameterCode.UPDATE_TIME, ParameterCode.DEGREE, ParameterCode.WORK_YEARS]

    @staticmethod
    def __zhaopin_optional__():
        return [ParameterCode.CUR_POSITION, ParameterCode.WORK_STATUS, ParameterCode.GENDER, ParameterCode.EXP_PLACE]

    @staticmethod
    def __job_required__():
        pass

    @staticmethod
    def __job_optional__():
        pass



class ReasonCode(object):
    """
        帐号退出原因
    """
    # 结束原因： 0: 使用中 1: 正常退出(使用次数达到上限) 2: 任务系统主动关闭 3: 不能登录 4: 不能查询
    USING = 0
    NORMAL = 1
    TASK_CLOSE = 2
    LOGIN_ERROR = 3
    SEARCH_ERROR = 4
    CONDITION_ERROR = 5

    @staticmethod
    def format(code):
        reason_dict = {
            0: u"正在使用",
            1: u"正常退出(使用次数达到上限)",
            2: u"任务系统主动关闭",
            3: u"不能登录",
            4: u"不能查询",
            5: u"帐号查询条件不满足挖掘平台任务系统"
        }
        return reason_dict.get(code)



class RequestTypeCode(object):
    SEARCH = 0
    RESUME = 1
    UPLOAD = 2

    @staticmethod
    def format(code):
        code_dict = {
            0: u"查询",
            1: u"简历",
            2: u"上传"
        }
        return code_dict.get(code)
