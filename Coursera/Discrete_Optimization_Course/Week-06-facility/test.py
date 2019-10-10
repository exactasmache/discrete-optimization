from multiprocessing import Pool
import time


def func1(x):
    x += 2
    # time.sleep(15)
    return x

if __name__ == '__main__':
    with Pool(processes=3) as pool:
        x = 1
        r1 = pool.apply_async(func1, (x, ))

        try:
            x = r1.get(1)
        except:
            pass

    print(x)
        