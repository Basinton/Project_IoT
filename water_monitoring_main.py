import PrivateTasks.main_ui_task
import PrivateTasks.led_blinky_task
import PrivateTasks.water_monitoring_task
import PrivateTasks.rapido_server_task
import PrivateTasks.water_management_task

from Scheduler.scheduler import Scheduler

import Utilities.modbus485 as modbus485
from Utilities.softwaretimer import *
import time

# Adafruit IO credentials
AIO_USERNAME = 'BasintonDinh'
AIO_KEY = 'aio_lJNn76oEYsLN1H6KPjUp6m3HUKKk'

# Initialize the serial port once
modbus485.initialize_modbus()

if modbus485.ser:
    watermonitoring_timer = softwaretimer()

    scheduler = Scheduler()
    scheduler.SCH_Init()
    soft_timer = softwaretimer()

    ledblink_task = PrivateTasks.led_blinky_task.LedBlinkyTask()
    watermonitoring = PrivateTasks.water_monitoring_task.WaterMonitoringTask(watermonitoring_timer, modbus485, AIO_USERNAME, AIO_KEY)
    main_ui = PrivateTasks.main_ui_task.Main_UI(watermonitoring)
    rapidoserver = PrivateTasks.rapido_server_task.RapidoServerTask()
    water_management = PrivateTasks.water_management_task.WaterManagementTask(modbus485, lambda msg: print(f"Notification: {msg}"))

    scheduler.SCH_Add_Task(soft_timer.Timer_Run, 0, 1000)  # Run every second
    scheduler.SCH_Add_Task(ledblink_task.blink, 0, 1000)  # Blink every second
    scheduler.SCH_Add_Task(main_ui.UI_Refresh, 0, 100)    # Refresh UI every 100 ms
    scheduler.SCH_Add_Task(watermonitoring_timer.Timer_Run, 0, 100)  # Run timer every 100 ms
    scheduler.SCH_Add_Task(watermonitoring.WaterMonitoringTask_Run, 0, 1000)  # Run every second
    scheduler.SCH_Add_Task(water_management.run, 0, 1000)  # Run every second

    while True:
        scheduler.SCH_Update()
        scheduler.SCH_Dispatch_Tasks()
        time.sleep(0.1)
else:
    print("Serial port is not available. Cannot proceed with setting devices.")
