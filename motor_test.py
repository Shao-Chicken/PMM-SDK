#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import os
from motor_control import MotorController

def test_position_mode(motor):
    """测试轮廓位置模式"""
    print("\n---开始测试轮廓位置模式---")
    
    # 设置轮廓位置模式
    if not motor.set_profile_position_mode():
        print(f"设置轮廓位置模式失败，状态: {motor.status}")
        return False
    
    # 设置运动参数
    motor.set_motion_parameters(velocity=5.0, accel=10.0, decel=10.0)
    
    # 使能电机
    if not motor.enable_motor():
        print(f"使能电机失败，状态: {motor.status}")
        return False
        
    # 释放刹车
    motor.release_brake()
    
    # 测试相对位置移动
    print("执行相对位置移动 +10.0 单位...")
    motor.move_by_distance(10.0)
    
    # 等待运动完成
    if motor.wait_target_reached(timeout=5.0):
        print("相对位置移动完成")
        status = motor.get_motor_status()
        if status:
            print(f"当前位置: {status[1]}, 当前速度: {status[2]}")
    else:
        print(f"运动超时，状态: {motor.status}")
    
    time.sleep(1.0)
    
    # 测试绝对位置移动
    print("执行绝对位置移动到 0.0 单位...")
    motor.move_to_position(0.0)
    
    # 等待运动完成
    if motor.wait_target_reached(timeout=5.0):
        print("绝对位置移动完成")
        status = motor.get_motor_status()
        if status:
            print(f"当前位置: {status[1]}, 当前速度: {status[2]}")
    else:
        print(f"运动超时，状态: {motor.status}")
    
    # 吸合刹车
    motor.engage_brake()
    
    # 脱机电机
    motor.disable_motor()
    
    print("---轮廓位置模式测试完成---")
    return True

def test_velocity_mode(motor):
    """测试轮廓速度模式"""
    print("\n---开始测试轮廓速度模式---")
    
    # 设置轮廓速度模式
    if not motor.set_profile_velocity_mode():
        print(f"设置轮廓速度模式失败，状态: {motor.status}")
        return False
    
    # 设置运动参数
    motor.set_motion_parameters(velocity=5.0, accel=10.0, decel=10.0)
    
    # 使能电机
    if not motor.enable_motor():
        print(f"使能电机失败，状态: {motor.status}")
        return False
        
    # 释放刹车
    motor.release_brake()
    
    # 测试正向运动
    print("执行正向速度运动，速度 +3.0 单位/s...")
    motor.run_velocity(3.0)
    
    # 监控速度一段时间
    for i in range(5):
        time.sleep(0.5)
        status = motor.get_motor_status()
        if status:
            print(f"当前位置: {status[1]}, 当前速度: {status[2]}")
    
    # 测试反向运动
    print("执行反向速度运动，速度 -3.0 单位/s...")
    motor.run_velocity(-3.0)
    
    # 监控速度一段时间
    for i in range(5):
        time.sleep(0.5)
        status = motor.get_motor_status()
        if status:
            print(f"当前位置: {status[1]}, 当前速度: {status[2]}")
    
    # 停止运动
    print("停止电机...")
    motor.run_velocity(0.0)
    
    # 等待电机停止
    time.sleep(1.0)
    status = motor.get_motor_status()
    if status:
        print(f"当前位置: {status[1]}, 当前速度: {status[2]}")
    
    # 吸合刹车
    motor.engage_brake()
    
    # 脱机电机
    motor.disable_motor()
    
    print("---轮廓速度模式测试完成---")
    return True

def test_brake_control(motor):
    """测试刹车控制"""
    print("\n---开始测试刹车控制---")
    
    # 设置轮廓位置模式
    if not motor.set_profile_position_mode():
        print(f"设置轮廓位置模式失败，状态: {motor.status}")
        return False
    
    # 使能电机
    if not motor.enable_motor():
        print(f"使能电机失败，状态: {motor.status}")
        return False
    
    # 测试释放刹车
    print("释放刹车...")
    motor.release_brake()
    time.sleep(1.0)
    print("刹车已释放，此时电机轴应可自由转动")
    
    # 测试吸合刹车
    print("吸合刹车...")
    motor.engage_brake()
    time.sleep(1.0)
    print("刹车已吸合，此时电机轴应被锁定")
    
    # 再次测试释放刹车
    print("再次释放刹车...")
    motor.release_brake()
    time.sleep(1.0)
    print("刹车已释放，此时电机轴应可自由转动")
    
    # 最后吸合刹车
    print("最后吸合刹车...")
    motor.engage_brake()
    
    # 脱机电机
    motor.disable_motor()
    
    print("---刹车控制测试完成---")
    return True

def main():
    """主函数"""
    sdk_path = r"G:/Motor/NiMServoSDK-MM 目标文件V1.1.0/NiMServoSDK-MM 目标文件V1.1.0/NimServoSDK-MM-bin-Windows-X64/NimServoSDK-MM-bin-Windows-X64/bin"
    
    # 将参数文件和DLL路径添加到Python搜索路径
    param_path = os.path.dirname(os.path.abspath(__file__))
    
    # 复制参数文件到当前目录
    param_db = "CANopen.db"
    if not os.path.exists(os.path.join(param_path, param_db)):
        import shutil
        try:
            shutil.copy2(os.path.join(sdk_path, param_db), param_path)
            print(f"已复制参数文件 {param_db} 到当前目录")
        except Exception as e:
            print(f"警告: 无法复制参数文件: {e}")
    
    # SDK路径为None时使用当前目录
    print(f"使用SDK路径: {sdk_path}")
    motor = MotorController(sdk_path=sdk_path, comm_type=0, node_id=1)
    
    # 连接CANopen设备
    # 根据实际情况调整参数
    if not motor.connect_canopen(dev_type="1001", dev_index=0, baudrate=8):
        print(f"连接CANopen设备失败，状态: {motor.status}")
        motor.close()
        return
    
    # 初始化电机
    if not motor.initialize_motor(param_db=param_db, unit_factor=10000.0):
        print(f"初始化电机失败，状态: {motor.status}")
        motor.close()
        return
    
    try:
        # 测试轮廓位置模式
        test_position_mode(motor)
        
        # 暂停一下再进行下一个测试
        time.sleep(1.0)
        
        # 测试轮廓速度模式
        test_velocity_mode(motor)
        
        # 暂停一下再进行下一个测试
        time.sleep(1.0)
        
        # 测试刹车控制
        test_brake_control(motor)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试出现异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭连接
        print("\n关闭电机控制器...")
        motor.close()
        print(f"最终状态: {motor.status}")

if __name__ == "__main__":
    main() 