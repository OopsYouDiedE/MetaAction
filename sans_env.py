import gym
from gym import spaces
from playwright.sync_api import sync_playwright
import numpy as np
import cv2
import time


class SansFightEnv(gym.Env):
    """
    自定义 Gym 环境，使用 Playwright 与 https://jcw87.github.io/c2-sans-fight/ 交互。
    输入：W, A, S, D, Enter（动作空间为 5 个独立按键，0=释放，1=按下）
    输出：屏幕截图（观察空间为 RGB 图像），使用 Playwright 获取。
    """

    def __init__(self):
        super(SansFightEnv, self).__init__()

        # 初始化 Playwright 和浏览器
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False)  # headless=False 以便调试
        self.page = self.browser.new_page()
        self.page.goto("https://jcw87.github.io/c2-sans-fight/")

        # 等待页面加载完成
        time.sleep(5)

        # 设置动作空间（5 个独立按键，每个按键有 0 或 1 两种状态）
        self.action_space = spaces.MultiBinary(5)  # [W, A, S, D, Enter]

        # 获取初始屏幕截图以确定观察空间的尺寸
        img = self._get_screenshot()
        height, width, _ = img.shape
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(height, width, 3), dtype=np.uint8
        )

        # 定义按键映射
        self.key_map = {
            0: "w",       # 上
            1: "a",       # 左
            2: "s",       # 下
            3: "d",       # 右
            4: "Enter"    # 确认
        }

        # 追踪当前按键状态
        self.key_states = [0] * 5  # 初始状态均为释放

    def reset(self):
        """
        重置环境到初始状态。
        按下 Enter 键开始游戏，返回初始屏幕截图。
        """
        # 重置按键状态
        self.key_states = [0] * 5
        # 模拟按下 Enter 键以开始游戏
        self.page.keyboard.press("Enter")
        time.sleep(1)  # 等待游戏开始
        return self._get_screenshot()

    def step(self, action):
        """
        执行一个动作，模拟按键输入，并返回新的观察、奖励、是否结束和额外信息。
        action: [W, A, S, D, Enter]，每个值为 0（释放）或 1（按下）
        """
        # 遍历每个按键，更新状态
        for i, (new_state, old_state) in enumerate(zip(action, self.key_states)):
            key = self.key_map[i]
            if new_state == 1 and old_state == 0:
                # 从释放变为按下
                self.page.keyboard.down(key)
            elif new_state == 0 and old_state == 1:
                # 从按下变为释放
                self.page.keyboard.up(key)
            # 如果状态未改变，则保持不变

        # 更新按键状态
        self.key_states = action.copy()

        # 等待一小段时间以模拟按键效果
        time.sleep(1/30)

        # 获取新的屏幕截图作为观察
        observation = self._get_screenshot()

        # 暂时设置奖励和 done（需要根据游戏逻辑进一步定义）
        reward = 0
        done = False
        info = {}

        return observation, reward, done, info

    def render(self, mode='human'):
        """
        使用 OpenCV 显示当前屏幕截图。
        """
        img = self._get_screenshot()
        cv2.imshow("Sans Fight", img)
        cv2.waitKey(1)  # 短暂等待以显示窗口

    def _get_screenshot(self):
        """
        使用 Playwright 获取当前页面截图并转换为 NumPy 数组。
        """
        screenshot_bytes = self.page.screenshot()
        # 使用 OpenCV 解码 PNG 数据
        img = cv2.imdecode(np.frombuffer(
            screenshot_bytes, np.uint8), cv2.IMREAD_COLOR)
        # 将 BGR 转换为 RGB
        img = img[:, :, ::-1]
        return img

    def close(self):
        """
        关闭环境，释放 Playwright 资源。
        """
        self.browser.close()
        self.playwright.stop()
        cv2.destroyAllWindows()  # 关闭 OpenCV 窗口


# 使用示例
if __name__ == "__main__":
    # 创建环境
    env = SansFightEnv()

    # 重置环境
    observation = env.reset()
    for _ in range(30):
        # 执行一系列动作（例如按下 W 和 A，释放其他键）
        action = [0, 0, 0, 0, 1]  # [W=按下, A=按下, S=释放, D=释放, Enter=释放]
        observation, reward, done, info = env.step(action)
        env.render()

    # 训练结束后关闭环境
    time.sleep(2)  # 等待片刻以观察效果
    env.close()
