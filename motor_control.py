#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes, os, types, sys, time
from NimServoSDK import *

class MotorController:
    def __init__(self, sdk_path=None, comm_type=0, node_id=1):
        """
        初始化电机控制器
        参数:
        sdk_path - SDK库路径，默认为None(使用当前路径)
        comm_type - 通信方式：0-CANopen, 1-EtherCAT, 2-Modbus
        node_id - 电机节点ID
        """
        self.h_master = None
        self.node_id = node_id
        self.status = "未初始化"
        
        # 将SDK路径添加到系统搜索路径中
        if sdk_path is not None:
            os.environ['PATH'] = sdk_path + os.pathsep + os.environ['PATH']
            
        # 初始化SDK
        if sdk_path is None:
            Nim_init(".")
        else:
            Nim_init(sdk_path)
        
        # 设置日志标志 (SDK已初始化，现在可以设置了)
        Nim_setLogFlags(1)
            
        # 创建主站
        [res, h_master] = Nim_create_master(comm_type)
        if res == 0:
            self.h_master = h_master
            self.status = "主站创建成功"
        else:
            self.status = f"主站创建失败，错误码: {res}"
    
    def connect_canopen(self, dev_type="1001", dev_index=0, baudrate=8, pdo_interval=10, sync_interval=10):
        """
        连接CANopen设备
        参数:
        dev_type - 设备类型，默认"1001"
        dev_index - 设备索引，默认0
        baudrate - 波特率，默认8 (1000K)
        pdo_interval - PDO间隔时间，默认10ms
        sync_interval - 同步间隔时间，默认10ms
        """
        if self.h_master is None:
            self.status = "主站未创建，无法连接"
            return False
            
        conn_str = f'{{"DevType": "{dev_type}", "DevIndex": {dev_index}, "Baudrate": {baudrate}, "PDOIntervalMS": {pdo_interval}, "SyncIntervalMS": {sync_interval}}}'
        res = Nim_master_run(self.h_master, conn_str)
        if res == 0:
            self.status = "CANopen连接成功"
            return True
        else:
            self.status = f"CANopen连接失败，错误码: {res}"
            return False
            
    def initialize_motor(self, param_db="CANopen.db", unit_factor=10000.0):
        """
        初始化电机，包括扫描节点、加载参数、读取PDO配置等
        参数:
        param_db - 参数数据库文件名
        unit_factor - 用户单位换算系数
        """
        if self.h_master is None:
            self.status = "主站未创建，无法初始化电机"
            return False
            
        # 进入预操作模式
        Nim_master_changeToPreOP(self.h_master)
        time.sleep(0.05)
        
        # 扫描节点
        Nim_scan_nodes(self.h_master, 1, 10)
        
        # 检查节点是否在线
        if 1 != Nim_is_online(self.h_master, self.node_id):
            self.status = f"电机节点{self.node_id}不在线"
            return False
            
        # 加载参数、配置
        Nim_load_params(self.h_master, self.node_id, param_db)
        Nim_read_PDOConfig(self.h_master, self.node_id)
        Nim_set_unitsFactor(self.h_master, self.node_id, unit_factor)
        Nim_clearError(self.h_master, self.node_id, 1)
        
        # 切换到操作模式
        Nim_master_changeToOP(self.h_master)
        time.sleep(0.05)
        
        self.status = "电机初始化成功"
        return True
        
    def enable_motor(self):
        """
        使能电机（抱机）
        """
        if self.h_master is None:
            self.status = "主站未创建，无法使能电机"
            return False
            
        Nim_power_on(self.h_master, self.node_id, 1)
        time.sleep(0.2)  # 必要延时
        
        # 检查电机状态
        [res, sw] = Nim_get_statusWord(self.h_master, self.node_id, 0)
        if res == 0 and (sw & 0x6F) == 0x27:  # 检查电机是否处于使能状态
            self.status = "电机使能成功"
            return True
        else:
            self.status = f"电机使能失败，状态字: {sw}"
            return False
            
    def disable_motor(self):
        """
        脱机电机（释放电机）
        """
        if self.h_master is None:
            self.status = "主站未创建，无法脱机电机"
            return False
            
        Nim_power_off(self.h_master, self.node_id, 1)
        time.sleep(0.05)  # 必要延时
        
        self.status = "电机脱机成功"
        return True
        
    def set_profile_velocity_mode(self):
        """
        设置为轮廓速度模式(PV)
        """
        if self.h_master is None:
            self.status = "主站未创建，无法设置模式"
            return False
            
        # 先脱机电机
        Nim_power_off(self.h_master, self.node_id, 1)
        time.sleep(0.05)
        
        # 设置轮廓速度模式
        Nim_set_workMode(self.h_master, self.node_id, ServoWorkMode.SERVO_PV_MODE, 1)
        time.sleep(0.05)
        
        # 获取工作模式确认
        [res, mode] = Nim_get_workModeDisplay(self.h_master, self.node_id, 1)
        if res == 0 and mode == ServoWorkMode.SERVO_PV_MODE:
            self.status = "设置轮廓速度模式成功"
            return True
        else:
            self.status = f"设置轮廓速度模式失败，当前模式: {mode}"
            return False
            
    def set_profile_position_mode(self):
        """
        设置为轮廓位置模式(PP)
        """
        if self.h_master is None:
            self.status = "主站未创建，无法设置模式"
            return False
            
        # 先脱机电机
        Nim_power_off(self.h_master, self.node_id, 1)
        time.sleep(0.05)
        
        # 设置轮廓位置模式
        Nim_set_workMode(self.h_master, self.node_id, ServoWorkMode.SERVO_PP_MODE, 1)
        time.sleep(0.05)
        
        # 获取工作模式确认
        [res, mode] = Nim_get_workModeDisplay(self.h_master, self.node_id, 1)
        if res == 0 and mode == ServoWorkMode.SERVO_PP_MODE:
            self.status = "设置轮廓位置模式成功"
            return True
        else:
            self.status = f"设置轮廓位置模式失败，当前模式: {mode}"
            return False
            
    def set_motion_parameters(self, velocity=10.0, accel=12.5, decel=12.5):
        """
        设置运动参数 (速度、加速度、减速度)
        参数:
        velocity - 轮廓速度 (用户单位/s)
        accel - 加速度 (用户单位/s^2)
        decel - 减速度 (用户单位/s^2)
        """
        if self.h_master is None:
            self.status = "主站未创建，无法设置参数"
            return False
            
        Nim_set_profileVelocity(self.h_master, self.node_id, velocity)
        Nim_set_profileAccel(self.h_master, self.node_id, accel)
        Nim_set_profileDecel(self.h_master, self.node_id, decel)
        
        self.status = "运动参数设置成功"
        return True
        
    def run_velocity(self, velocity):
        """
        执行速度运动 (轮廓速度模式下)
        参数:
        velocity - 目标速度，正值正转，负值反转 (用户单位/s)
        """
        if self.h_master is None:
            self.status = "主站未创建，无法执行运动"
            return False
            
        # 获取当前模式
        [res, mode] = Nim_get_workModeDisplay(self.h_master, self.node_id, 0)
        if res != 0 or mode != ServoWorkMode.SERVO_PV_MODE:
            self.status = f"非轮廓速度模式，当前模式: {mode}"
            return False
            
        # 根据正负值决定正转或反转
        if velocity > 0:
            Nim_forward(self.h_master, self.node_id, velocity, 0)
        elif velocity < 0:
            Nim_backward(self.h_master, self.node_id, abs(velocity), 0)
        else:
            # 速度为0时停止
            Nim_forward(self.h_master, self.node_id, 0.0, 0)
            
        self.status = f"速度运动指令已发送，目标速度: {velocity}"
        return True
        
    def move_to_position(self, position, immediate=True):
        """
        移动到指定位置 (轮廓位置模式下的绝对位置移动)
        参数:
        position - 目标位置 (用户单位)
        immediate - 是否立即更新，True为立即更新，False为非立即更新
        """
        if self.h_master is None:
            self.status = "主站未创建，无法执行运动"
            return False
            
        # 获取当前模式
        [res, mode] = Nim_get_workModeDisplay(self.h_master, self.node_id, 0)
        if res != 0 or mode != ServoWorkMode.SERVO_PP_MODE:
            self.status = f"非轮廓位置模式，当前模式: {mode}"
            return False
            
        Nim_moveAbsolute(self.h_master, self.node_id, position, 1 if immediate else 0, 0)
        self.status = f"位置运动指令已发送，目标位置: {position}"
        return True
        
    def move_by_distance(self, distance, immediate=True):
        """
        移动指定距离 (轮廓位置模式下的相对位置移动)
        参数:
        distance - 移动距离 (用户单位)
        immediate - 是否立即更新，True为立即更新，False为非立即更新
        """
        if self.h_master is None:
            self.status = "主站未创建，无法执行运动"
            return False
            
        # 获取当前模式
        [res, mode] = Nim_get_workModeDisplay(self.h_master, self.node_id, 0)
        if res != 0 or mode != ServoWorkMode.SERVO_PP_MODE:
            self.status = f"非轮廓位置模式，当前模式: {mode}"
            return False
            
        Nim_moveRelative(self.h_master, self.node_id, distance, 1 if immediate else 0, 0)
        self.status = f"相对位置运动指令已发送，移动距离: {distance}"
        return True
    
    def release_brake(self):
        """
        释放电机刹车
        使用DO输出控制刹车，通常为高电平释放刹车
        """
        if self.h_master is None:
            self.status = "主站未创建，无法控制刹车"
            return False
            
        # 设置数字输出，假设DO1控制刹车，1为释放刹车
        # 根据实际刹车连接的DO端口和电平逻辑调整
        Nim_set_DOs(self.h_master, self.node_id, 0x01, 1)  # 设置DO1为高电平
        time.sleep(0.1)  # 等待刹车释放
        
        self.status = "刹车已释放"
        return True
        
    def engage_brake(self):
        """
        吸合电机刹车
        使用DO输出控制刹车，通常为低电平吸合刹车
        """
        if self.h_master is None:
            self.status = "主站未创建，无法控制刹车"
            return False
            
        # 设置数字输出，假设DO1控制刹车，0为吸合刹车
        # 根据实际刹车连接的DO端口和电平逻辑调整
        Nim_set_DOs(self.h_master, self.node_id, 0x00, 1)  # 设置DO1为低电平
        time.sleep(0.1)  # 等待刹车吸合
        
        self.status = "刹车已吸合"
        return True
        
    def quick_stop(self):
        """
        快速停止电机运动
        """
        if self.h_master is None:
            self.status = "主站未创建，无法停止电机"
            return False
            
        Nim_fastStop(self.h_master, self.node_id, 1)
        self.status = "电机快速停止指令已发送"
        return True
        
    def get_motor_status(self):
        """
        获取电机状态信息
        返回: [状态字, 当前位置, 当前速度]
        """
        if self.h_master is None:
            self.status = "主站未创建，无法获取状态"
            return None
            
        [res_sw, sw] = Nim_get_statusWord(self.h_master, self.node_id, 0)
        [res_pos, pos] = Nim_get_currentPosition(self.h_master, self.node_id, 0)
        [res_vel, vel] = Nim_get_currentVelocity(self.h_master, self.node_id, 0)
        
        if res_sw == 0 and res_pos == 0 and res_vel == 0:
            return [sw, pos, vel]
        else:
            self.status = "获取电机状态失败"
            return None
    
    def check_target_reached(self):
        """
        检查是否到达目标位置
        返回: True - 已到达目标位置; False - 未到达目标位置
        """
        [res, sw] = Nim_get_statusWord(self.h_master, self.node_id, 0)
        if res == 0 and (sw & 0x400) != 0:  # 检查目标到达位
            return True
        return False
            
    def wait_target_reached(self, timeout=10.0, interval=0.1):
        """
        等待电机到达目标位置
        参数:
        timeout - 超时时间(秒)
        interval - 检查间隔(秒)
        返回: True - 到达目标; False - 超时或其他错误
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_target_reached():
                return True
            time.sleep(interval)
        
        self.status = "等待目标到达超时"
        return False
        
    def close(self):
        """
        关闭连接并释放资源
        """
        if self.h_master is not None:
            # 先脱机电机
            Nim_power_off(self.h_master, self.node_id, 1)
            time.sleep(0.05)
            
            # 进入预操作模式
            Nim_master_changeToPreOP(self.h_master)
            time.sleep(0.05)
            
            # 停止主站并销毁
            Nim_master_stop(self.h_master)
            Nim_destroy_master(self.h_master)
            self.h_master = None
            
        # 清理SDK
        Nim_clean()
        self.status = "控制器已关闭" 