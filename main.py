# main.py

from data import ACTIVITIES, ROOMS, TIMES


def main():
    print("=== SLA Genetic Scheduler ===")
    print("This is a placeholder main function for CS 461 Program 2.\n")

    # 简单检查 data.py 是否正确加载
    print("Data summary:")
    print(f"- Activities: {len(ACTIVITIES)}")
    print(f"- Rooms:      {len(ROOMS)}")
    print(f"- Time slots: {len(TIMES)}")

    # 可选：打印前几个活动名字看看
    sample_activities = list(ACTIVITIES.keys())[:5]
    print(f"- Sample activities: {sample_activities}")


if __name__ == "__main__":
    main()
