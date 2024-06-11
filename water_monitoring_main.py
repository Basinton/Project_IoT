import time
import PrivateTasks.main_ui_task
import PrivateTasks.led_blinky_task
import PrivateTasks.water_monitoring_task
import PrivateTasks.rapido_server_task
import PrivateTasks.water_management_task

from Scheduler.scheduler import Scheduler
import Ultilities.modbus485 as modbus485
from Ultilities.softwaretimer import softwaretimer

AIO_USERNAME = 'BasintonDinh'
AIO_KEY = 'abc'
AIO_SCHEDULE_FEED = 'iot-project.app'
AIO_SENSOR_FEED = 'iot-project.gateway'
AIO_MANAGEMENT_FEED = 'iot-project.management'

# Initialize the serial port once
modbus485.initialize_modbus()

# Tạo instance của WaterManagementTask
watermanagement = None

if modbus485.ser:
    watermonitoring_timer = softwaretimer()

    scheduler = Scheduler()
    scheduler.SCH_Init()

    ledblink_task = PrivateTasks.led_blinky_task.LedBlinkyTask()
    watermonitoring = PrivateTasks.water_monitoring_task.WaterMonitoringTask(watermonitoring_timer, modbus485.ser, AIO_USERNAME, AIO_KEY, AIO_SENSOR_FEED)
    main_ui = PrivateTasks.main_ui_task.Main_UI(watermonitoring)
    rapidoserver = PrivateTasks.rapido_server_task.RapidoServerTask()
    watermanagement = PrivateTasks.water_management_task.WaterManagementTask(modbus485, main_ui.notification_func, AIO_USERNAME, AIO_KEY, AIO_SCHEDULE_FEED, AIO_MANAGEMENT_FEED)

    # scheduler.SCH_Add_Task(ledblink_task.run, 0, 1000)
    scheduler.SCH_Add_Task(watermonitoring.run, 0, 10000)  # Chạy task này mỗi 10 giây
    # scheduler.SCH_Add_Task(main_ui.run, 0, 5000)
    # scheduler.SCH_Add_Task(rapidoserver.run, 0, 5000)
    scheduler.SCH_Add_Task(watermanagement.run, 0, 500)

    print("Starting scheduler loop")
    try:
        while True:
            scheduler.SCH_Update()
            scheduler.SCH_Dispatch_Tasks()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Cleaning up GPIO")
        ledblink_task.cleanup()
else:
    print("Serial port is not available. Cannot proceed with monitoring.")
