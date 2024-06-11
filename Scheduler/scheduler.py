import time
from Scheduler.task import Task

class Scheduler:
    TICK = 10  # Giảm giá trị TICK để giảm độ trễ
    SCH_MAX_TASKS = 40
    SCH_tasks_G = []
    current_index_task = 0

    def __init__(self):
        self.current_index_task = 0

    def SCH_Init(self):
        self.current_index_task = 0
        self.SCH_tasks_G.clear()

    def SCH_Add_Task(self, pFunction, DELAY, PERIOD):
        if self.current_index_task < self.SCH_MAX_TASKS:
            aTask = Task(pFunction, DELAY / self.TICK, PERIOD / self.TICK)
            aTask.TaskID = self.current_index_task
            self.SCH_tasks_G.append(aTask)
            self.current_index_task += 1
        else:
            print("PrivateTasks are full!!!")

    def SCH_Update(self):
        for task in self.SCH_tasks_G:
            if task.Delay > 0:
                task.Delay -= 1
            else:
                task.Delay = task.Period
                task.RunMe += 1

    def SCH_Dispatch_Tasks(self):
        for task in self.SCH_tasks_G:
            if task.RunMe > 0:
                task.RunMe -= 1
                task.pTask()

    def SCH_Delete(self, task_id):
        self.SCH_tasks_G = [task for task in self.SCH_tasks_G if task.TaskID != task_id]

    def SCH_GenerateID(self):
        return -1

    def start(self):
        print("Starting scheduler loop")
        try:
            while True:
                self.SCH_Update()
                self.SCH_Dispatch_Tasks()
                time.sleep(self.TICK / 1000.0)  # Chờ một khoảng thời gian nhỏ để giảm tải CPU
        except KeyboardInterrupt:
            print("Scheduler stopped")

