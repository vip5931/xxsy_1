# __init__.py 为初始化加载文件

# 导入系统资源模块
from ascript.android.system import R
# 导入动作模块
from ascript.android import action
# 导入节点检索模块
from ascript.android import node
# 导入图色检索模块
from ascript.android import screen
import time
# 导入所有需要的类
from ascript.android.screen import FindImages, CompareColors, FindColors
import logging

# 修改日志配置，只使用控制台输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 只使用控制台输出
    ]
)

# 定义5个角色的固定坐标位置
ROLE_POSITIONS = [
    {"x": 96, "y": 81},    # 第1个角色位置
    {"x": 96, "y": 196},   # 第2个角色位置
    {"x": 96, "y": 310},   # 第3个角色位置
    {"x": 96, "y": 423},   # 第4个角色位置
    {"x": 96, "y": 534},   # 第5个角色位置
]

current_role = 0  # 当前角色索引
in_menpai = False  # 是否已经在门派中

TASK_PRIORITIES = {
    "省电模式": 100,
    "奖励弹窗": 90,
    "排行榜": 80,
    "飞升提示": 70,
    "游戏公告": 60,
    "游历": 50,
    "游戏状态": 40,
    "门派任务": 30
}

CONFIG = {
    "等待时间": {
        "进入游戏": 10,
        "地图切换": 8,
        "按钮点击": 2,
        "奖励弹窗": 3
    },
    "图像识别": {
        "默认置信度": 0.8,
        "门派图标置信度": 0.5,
        "省电模式置信度": 0.4
    },
    "重试机制": {
        "最大重试次数": 3,
        "重试间隔": 2
    }
}

def get_current_task():
    """根据优先级返回当前应该执行的任务"""
    if FindImages.find_template(R.img("省电模式.png"), confidence=0.4):
        return "省电模式"
    # ... 其他任务检查 ...

def close_reward_popup():
    """
    检查并关闭获得物品弹窗
    Returns:
        bool: 是否找到并关闭了弹窗
    """
    # 检查特定颜色组合
    color_pattern = ('1006,273,#FDFDFB|1024,276,#FDFDFB|1024,292,#FDFDFB|'
                    '1008,290,#FDFDFB|1016,283,#FDFDFB|1016,276,#373031|'
                    '1014,290,#2D2628')
    
    if CompareColors.compare(color_pattern, diff=0.9):
        print("检测到获得物品弹窗，点击关闭")
        action.click(1015, 283)
        time.sleep(2)
        return True
    return False

def handle_mail():
    """处理邮件领取"""
    # 添加重试机制
    retry_count = 3
    while retry_count > 0:
        youjian = FindImages.find_template(R.img("邮件.png"), confidence=0.8)
        if youjian:
            break
        retry_count -= 1
        time.sleep(2)
    if retry_count == 0:
        print("多次尝试未找到邮件按钮")
        return False
        
    print("找到邮件按钮，点击打开")
    action.click(youjian['center_x'], youjian['center_y'])
    time.sleep(3)
    
    # 检查是否是未全选状态
    weixuanzhong = FindImages.find_template(R.img("未选中状态.png"), confidence=0.8)
    if weixuanzhong:
        print("邮件未全选，点击全选")
        action.click(weixuanzhong['center_x'], weixuanzhong['center_y'])
        time.sleep(2)
        
        # 验证是否变成全选状态
        quanxuan = FindImages.find_template(R.img("全选状态.png"), confidence=0.8)
        if not quanxuan:
            print("全选失败")
            return False
    
    # 点击领取选中
    lingqu = FindImages.find_template(R.img("领取选中.png"), confidence=0.8)
    if not lingqu:
        print("没找到领取选中按钮")
        return False
        
    print("点击领取选中")
    action.click(lingqu['center_x'], lingqu['center_y'])
    time.sleep(3)
    
    # 点击同意领取选中
    tongyi = FindImages.find_template(R.img("同意领取选中.png"), confidence=0.8)
    if tongyi:
        print("点击同意领取选中")
        action.click(tongyi['center_x'], tongyi['center_y'])
        time.sleep(3)
        
        # 处理奖励弹窗
        while True:
            if not close_reward_popup():
                break
            time.sleep(3)
    
    # 关闭邮件弹窗
    close_btn = FindImages.find_template(R.img("关闭邮件弹窗.png"), confidence=0.8)
    if close_btn:
        print("关闭邮件弹窗")
        action.click(close_btn['center_x'], close_btn['center_y'])
        time.sleep(3)
    
    return True

def do_map_and_mail():
    """处理地图和邮件任务"""
    # 检查并打开地图
    ditu = FindImages.find_template(R.img("地图.png"), confidence=0.8)
    if not ditu:
        return False
        
    print("找到地图按钮，点击打开")
    action.click(ditu['center_x'], ditu['center_y'])
    time.sleep(3)
    
    # 检查当前是否在风云劫境
    xiaosangcun = FindImages.find_template(R.img("风云劫境.png"), confidence=0.8)
    if not xiaosangcun:
        print("不在风云劫境，切换地图")
        action.click(52, 207)
        time.sleep(3)
        action.click(518,536)
        time.sleep(8)
        action.click(1034,558)
        time.sleep(8)
    else:
        print("已在风云劫境，关闭地图")
        action.click(1230, 103)
        time.sleep(3)
    
    # 处理邮件
    return handle_mail()

def check_and_do_basic_tasks():
    """检查并执行基础任务(地图传送和邮件领取)"""
    # 检查是否刚进入游戏
    if FindImages.find_template(R.img("地图.png"), confidence=0.8):
        do_map_and_mail()  # 执行但不返回结果
        return False  # 继续执行后续任务
    return False

def handle_game_state():
    """处理游戏状态，返回是否需要继续检查"""
    global in_menpai  # 声明使用全局变量
    
    # 1. 选择角色界面
    select_role = CompareColors.compare('97,649,#D2B471|105,669,#C6A461|131,681,#A47633|110,657,#BE9A56|93,660,#D8BC79', diff=0.9)
    if select_role:
        print("在选择角色界面")
        result2 = FindImages.find_template(R.img("进入游戏2.png"), confidence=0.8)
        if result2:
            role = ROLE_POSITIONS[current_role]
            print(f"选择第{current_role + 1}号角色")
            action.click(role['x'], role['y'])
            time.sleep(3)
            action.click(result2['center_x'], result2['center_y'])
            time.sleep(10)
            in_menpai = False
            return True
            
    # 2. 进入游戏按钮
    result = FindImages.find_template(R.img("进入游戏.png"), confidence=0.8)
    if result:
        print("点击进入游戏")
        action.click(result['center_x'], result['center_y'])
        time.sleep(10)
        return True
        
    # 3. 地图和邮件任务
    check_and_do_basic_tasks()  # 执行但不影响流程
    return False  # 继续执行后续任务

def check_qiandao_status():
    """
    检查签到状态
    Returns:
        tuple: (普通签到是否完成, 豪华签到是否完成)
    """
    # 检查普通签到状态
    putong_done = FindColors.find('711,182,#A3A3A3|748,182,#979797|776,182,#959593|732,194,#EDEDEB|758,191,#FDFDFB|767,204,#848484',
                                 rect=[680,149,798,243], ori=1)
    
    # 检查豪华签到状态
    haohua_done = FindColors.find('1071,180,#A5A5A3|1109,182,#979797|1140,183,#AFAFAF|1088,198,#F9F9F7|1113,199,#F5F5F3|1124,203,#FBFBFB|1098,215,#B3B3B3|1094,198,#F9F9F7|1072,215,#A9A9A7',
                                 rect=[1027,138,1167,247], ori=1)
    
    return putong_done, haohua_done

def handle_menpai_tasks():
    """处理门派相关任务，返回是否需要继续检查"""
    global in_menpai, current_role
    
    logging.info(f"处理角色 {current_role + 1} 的门派任务")
    
    # 初始化任务状态变量
    putong_signed = False
    haohua_signed = False
    juanxian_done = False
    yaoqianshu = False
    
    # 如果不在门派界面内，寻找门派图标
    if not in_menpai:
        menpai = FindImages.find_template(R.img("门派.png"), confidence=0.5)
        if menpai:
            print("找到门派图标")
            action.click(menpai['center_x'], menpai['center_y'])
            time.sleep(2)
            in_menpai = True
            return True
        else:
            print("没找到门派图标")
            arrow = FindImages.find_template(R.img("下箭头.png"), confidence=0.8)
            if arrow:
                print("找到下箭头")
                action.click(arrow['center_x'], arrow['center_y'])
                time.sleep(2)
                return True
    
    # 检查在门派界面内并执行门派任务
    menpai_in = FindImages.find_template(R.img("门派界面内.png"), confidence=0.8)
    if menpai_in:
        print("已在门派界面内")
        
        # 1) 检查签到状态
        putong_signed, haohua_signed = check_qiandao_status()
        
        # 处理普通签到
        if not putong_signed:
            print("普通签到未完成")
            # 检查普通签到按钮
            if FindColors.find('712,180,#5BB57C|748,180,#4CAB75|777,181,#49A570|778,215,#68C384|750,214,#5CBB7D|718,214,#5CBB7D|733,197,#F9FBF7|752,192,#6D9D80|736,200,#4F8B66',
                             rect=[670,143,834,245], ori=1, space=10):
                print("点击普通签到")
                action.click(745, 197)  # 点击普通签到按钮
                time.sleep(2)
                
                # 处理可能的奖励弹窗
                while True:
                    if not close_reward_popup():
                        break
                    time.sleep(2)
        else:
            print("普通签到已完成")
            
        # 处理豪华签到
        if not haohua_signed:
            print("豪华签到未完成")
            # 检查豪华签到按钮
            if FindColors.find('1074,182,#59B17A|1101,181,#49A774|1125,182,#49A771|1123,198,#F1F5F3|1097,212,#5BB97D|1093,197,#F9FBF7|1085,206,#FBFBFB|1139,213,#66C180', ori=1):
                print("点击豪华签到")
                action.click(1107, 197)  # 点击豪华签到按钮
                time.sleep(2)
                
                # 点击同意按钮
                tongyi = FindImages.find_template(R.img("同意.png"), confidence=0.8)
                if tongyi:
                    print("点击同意按钮")
                    action.click(tongyi['center_x'], tongyi['center_y'])
                    time.sleep(2)
                
                # 处理可能的奖励弹窗
                while True:
                    if not close_reward_popup():
                        break
                    time.sleep(2)
        else:
            print("豪华签到已完成")
        
        # 2) 检查门派捐献
        juanxian_done = FindImages.find_template(R.img("捐献已完成.png"), confidence=0.8)
        if not juanxian_done:
            print("门派捐献未完成，寻找参加按钮")
            canjia = FindImages.find_template(R.img("参加.png"), confidence=0.8)
            if canjia:
                print("找到参加按钮，点击参加")
                action.click(canjia['center_x'], canjia['center_y'])
                time.sleep(2)
                
                # 查找并点击捐献50按钮五次
                juanxian50 = FindImages.find_template(R.img("捐献50.png"), confidence=0.8)
                if juanxian50:
                    print("找到捐献50按钮，点击5次")
                    for i in range(5):
                        action.click(juanxian50['center_x'], juanxian50['center_y'])
                        print(f"第{i+1}次点击捐献50")
                        time.sleep(0.5)
                    
                    # 点击指定坐标
                    print("点击确认坐标")
                    action.click(1036, 125)
                    time.sleep(2)
                    
        
        # 3) 检查摇钱树
        yaoqianshu = FindImages.find_template(R.img("摇钱树检测.png"), confidence=0.8)
        if yaoqianshu:
            print("找到摇钱树，点击参加")
            canjia = FindImages.find_template(R.img("摇钱树参加.png"), confidence=0.9)
            if canjia:
                print("找到参加按钮，点击参加")
                action.click(canjia['center_x'], canjia['center_y'])
                time.sleep(2)
                
                # 点击指定坐标
                print("点击摇钱树位置")
                action.click(487, 636)
                time.sleep(2)

                queren = FindImages.find_template(R.img("摇钱树确认.png"), confidence=0.9)
                if queren:
                    print("点击确认按钮")
                    action.click(queren['center_x'], queren['center_y'])
                    time.sleep(2)
                
                # 查找并点击抽取十次按钮
                choushi = FindImages.find_template(R.img("抽取十次.png"), confidence=0.9)
                if choushi:
                    print("点击抽取十次")
                    action.click(choushi['center_x'], choushi['center_y'])
                    time.sleep(2)
                    
                    # 查找并点击确认按钮
                        
                        # 循环检测完成状态
                    while True:
                            wancheng = FindImages.find_template(R.img("摇钱树完成.png"), confidence=0.9)
                            if wancheng:
                                print("摇钱树完成，点击关闭")
                                action.click(1212, 69)
                                time.sleep(2)
                                break
                            time.sleep(2)
                wancheng = FindImages.find_template(R.img("摇钱树完成.png"), confidence=0.9)
                if wancheng:
                        print("摇钱树完成，点击关闭")
                        action.click(1212, 69)
                        time.sleep(2)
        
        # 如果三个任务都完成了，切换下一个角色
        if putong_signed and haohua_signed and juanxian_done and not yaoqianshu:
            print("所有任务完成，切换下一个角色")
            # 点击返回初始页面
            print("点击返回初始页面")
            action.click(1216, 72)
            time.sleep(2)  # 等待返回动画
            
            # 寻找设置图标
            shezhi = FindImages.find_template(R.img("设置图标.png"), confidence=0.8)
            if shezhi:
                print("找到设置图标，点击设置")
                action.click(shezhi['center_x'], shezhi['center_y'])
                time.sleep(2)
            else:
                # 如果没找到设置图标，尝试切换到设置
                qiehuan = FindImages.find_template(R.img("切换到设置.png"), confidence=0.8)
                if qiehuan:
                    print("点击切换到设置")
                    action.click(qiehuan['center_x'], qiehuan['center_y'])
                    time.sleep(2)
                    
                    # 再次寻找设置图标
                    shezhi = FindImages.find_template(R.img("设置图标.png"), confidence=0.8)
                    if shezhi:
                        print("找到设置图标，点击设置")
                        action.click(shezhi['center_x'], shezhi['center_y'])
                        time.sleep(2)
            
            # 点击切换账号
            qiehuan_account = FindImages.find_template(R.img("切换账号.png"), confidence=0.8)
            if qiehuan_account:
                print("点击切换账号")
                action.click(qiehuan_account['center_x'], qiehuan_account['center_y'])
                time.sleep(2)
                
                # 点击确认切换账号
                print("点击确认切换账号")
                action.click(729, 496)
                time.sleep(3)  # 等待切换账号动画
            
            current_role = (current_role + 1) % len(ROLE_POSITIONS)
            in_menpai = False  # 重置门派状态，准备下一个角色
    # 5. 如果不在门派界面内，寻找门派图标
    elif not in_menpai:
        menpai = FindImages.find_template(R.img("门派.png"), confidence=0.5)
        if menpai:
            print("找到门派图标")
            action.click(menpai['center_x'], menpai['center_y'])
            time.sleep(2)
            in_menpai = True
        else:
            print("没找到门派图标")
            arrow = FindImages.find_template(R.img("下箭头.png"), confidence=0.8)
            if arrow:
                print("找到下箭头")
                action.click(arrow['center_x'], arrow['center_y'])
                time.sleep(2)
    
    # 添加任务完成状态的全局变量
    global menpai_tasks_done
    
    # 添加任务计数
    tasks_completed = 0
    if putong_signed and haohua_signed:  # 两种签到都完成
        tasks_completed += 1
        logging.info("签到任务已完成")
    if juanxian_done:  # 捐献完成
        tasks_completed += 1
        logging.info("捐献任务已完成")
    if not yaoqianshu:  # 摇钱树完成
        tasks_completed += 1
        logging.info("摇钱树任务已完成")
    
    return False

def find_image_with_retry(image_name, confidence=0.8, retries=3):
    """通用的图像查找函数，带重试机制"""
    for i in range(retries):
        result = FindImages.find_template(R.img(image_name), confidence=confidence)
        if result:
            return result
        time.sleep(1)
    return None

while True:
    print("开始执行")
    
    # === 最高优先级：全局检测 ===
    if FindImages.find_template(R.img("省电模式.png"), confidence=0.4):
        print("检测到省电模式，点击屏幕中心")
        action.click(1260,701)
        time.sleep(2)
        continue
        
    if close_reward_popup():
        continue
        
    # 3. 检查排行榜隐藏按钮
    if FindImages.find_template(R.img("排行榜隐藏.png"), confidence=0.9):
        print("检测到排行榜隐藏按钮")
        if agree := FindImages.find_template(R.img("同意.png"), confidence=0.9):
            action.click(agree['center_x'], agree['center_y'])
            time.sleep(2)
        continue
    
    # 4. 检查飞升提示
    if feisheng := FindImages.find_template(R.img("飞升.png"), confidence=0.8):
        print("检测到飞升提示")
        if queding := FindImages.find_template(R.img("确定.png"), confidence=0.8):
            action.click(queding['center_x'], queding['center_y'])
            time.sleep(5)
            while True:
                if not close_reward_popup():
                    break
                time.sleep(2)
        continue
    
    # 5. 检查游戏公告
    if FindImages.find_template(R.img("游戏公告.png"), confidence=0.8):
        print("检测到游戏公告，点击关闭")
        action.click(1214, 72)
        time.sleep(2)
        continue
    
    # 6. 检查游历
    if FindImages.find_template(R.img("游历.png"), confidence=0.8):
        print("检测到游历，点击关闭")
        action.click(1212, 65)
        time.sleep(2)
        continue
    
    # === 中等优先级：游戏状态处理 ===
    if handle_game_state():
        continue
            
    # === 低优先级：门派任务处理 ===
    if handle_menpai_tasks():
        continue
    
    time.sleep(1)





