file1 = open('all-hard.out_summary.txt', 'r')
file2 = open('all-hard.out (1)_summary.txt', 'r')

counter1 = 0
counter2 = 0

for i in range(113):
    counter1 += int(file1.readline())
    counter2 += int(file2.readline())


print('with random max degree choice: ' + str(counter1))
print('with deterministic max degree choice: ' + str(counter2))