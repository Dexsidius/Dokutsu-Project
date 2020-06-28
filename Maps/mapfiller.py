def filling(s_x, s_y, w = 32, h = 32, count = 0):
    x = s_x
    y = s_y

    for i in range(20):
        x = s_x
        for j in range(20):
            file.write(str(x) + "-" + str(y) + "-" + str(w) + "-" + str(h)+ ",")
            y += 30
        s_x += 30
        y = s_y

    return 0
        
file = open('fill', 'w')
filling(277, 305)
file.close