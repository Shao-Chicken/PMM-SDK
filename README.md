# CANopen电机控制开发文档

## 开发进展

我们基于 NimServoSDK 开发了一个 Python 封装类 `MotorController`，用于简化基于 CANopen 协议的电机控制操作。目前已成功实现了基本的电机控制功能，包括轮廓位置模式、轮廓速度模式和刹车控制。

### 已完成功能

1. **初始化与连接**
   - SDK 初始化
   - CANopen 设备连接
   - 节点扫描和检测
   - 参数加载和配置

2. **工作模式控制**
   - 轮廓位置模式 (PP)
   - 轮廓速度模式 (PV)

3. **运动控制**
   - 位置运动控制（绝对位置、相对位置）
   - 速度运动控制（正转、反转、停止）

4. **刹车控制**
   - 释放刹车
   - 吸合刹车

5. **状态监控**
   - 电机状态获取
   - 位置和速度监控
   - 目标位置到达检测

### 测试结果

测试程序 `motor_test.py` 已经成功运行，验证了以下功能：

- 轮廓位置模式下的绝对位置和相对位置运动控制
- 轮廓速度模式下的正向和反向速度控制
- 刹车的释放和吸合操作

## 可用方法

`MotorController` 类提供了以下方法可供调用：

### 初始化和连接

```python
# 创建电机控制实例
motor = MotorController(sdk_path="路径/到/SDK", comm_type=0, node_id=1)

# 连接CANopen设备
motor.connect_canopen(dev_type="1001", dev_index=0, baudrate=8)

# 初始化电机
motor.initialize_motor(param_db="CANopen.db", unit_factor=10000.0)
```

### 电机基本控制

```python
# 使能电机
motor.enable_motor()

# 脱机电机
motor.disable_motor()

# 设置运动参数(速度、加速度、减速度)
motor.set_motion_parameters(velocity=10.0, accel=12.5, decel=12.5)

# 快速停止
motor.quick_stop()
```

### 工作模式设置

```python
# 设置轮廓位置模式
motor.set_profile_position_mode()

# 设置轮廓速度模式
motor.set_profile_velocity_mode()
```

### 位置控制

```python
# 移动到绝对位置
motor.move_to_position(position=100.0, immediate=True)

# 相对位置移动
motor.move_by_distance(distance=10.0, immediate=True)

# 等待目标位置到达
motor.wait_target_reached(timeout=5.0, interval=0.1)

# 检查是否到达目标位置
reached = motor.check_target_reached()
```

### 速度控制

```python
# 速度运动（正负值决定方向）
motor.run_velocity(velocity=5.0)  # 正向
motor.run_velocity(velocity=-5.0) # 反向
motor.run_velocity(velocity=0.0)  # 停止
```

### 刹车控制

```python
# 释放刹车
motor.release_brake()

# 吸合刹车
motor.engage_brake()
```

### 状态监测

```python
# 获取电机状态（状态字，当前位置，当前速度）
[sw, pos, vel] = motor.get_motor_status()
```

### 资源释放

```python
# 关闭并清理资源
motor.close()
```

## 开发建议

1. **错误处理**：
   - 所有方法都会返回操作是否成功的状态
   - 可以通过 `motor.status` 属性查看最新状态信息

2. **参数设置**：
   - 根据实际电机特性调整运动参数
   - 注意用户单位换算系数的影响

3. **刹车控制**：
   - 刹车控制假设使用DO1控制，高电平释放刹车，低电平吸合刹车
   - 根据实际硬件连接可能需要调整对应的DO端口和电平逻辑

4. **同步与异步操作**：
   - 对于位置运动，可以使用 `wait_target_reached` 等待运动完成
   - 对于速度运动，可以使用 `get_motor_status` 监控当前状态

## 后续开发计划

1. 添加更多工作模式的支持：
   - 循环同步位置模式 (CSP)
   - 循环同步速度模式 (CSV)
   - 循环同步转矩模式 (CST)

2. 增强错误处理和恢复机制

3. 优化多轴协调控制

4. 提供更多高级功能：
   - 轨迹规划
   - 多点运动
   - 电子齿轮比设置 
