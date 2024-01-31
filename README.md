- Изменить логику позиционирования стрелок, чтобы они были реально посередине.
- В set config добавить возможность изменять глобально arrowsize, dotsize, lw для процессов
  (dots_all=True, dots_size=8)
  (arrows_all=True, arrows_size=23)
- Постройка d.show() указать иные x,y чем задано. Например, строили p(V), а потом попросил d.show(x='volume', y='temperature') и он строит T(V).
- без вызова d.show() d.save() сохраняет какую-то фигню
- .xtick() и d.add_xticks() используют разный код для позиционирования штрихов
- Плохой расчет автоматического позиционирования и размеров подписей, штрихов, стрелочек
- Set globally process_arrow_size, process_dot_size (не могу т.к. у Process() нет доступа к конфигу)
- стрелки не посередине длины процесса
- iso_t, power, adiabatic не работают без at(), не берут конечную точку последнего процесса.
- рассчет координат без добавления на график. Вместо:
    d += (L1:= Linear().at(0.0, 0.4).to(10,0.4).lw(0) )
    d += (L2:= Linear().at(12,4).to(20,40).lw(0) )
    d += (B1:= Bezier().connect(L1,L2).lw(0))
    x,y = B1.get_coordinates()

    Это:
    L1 = Linear().at(0.0, 0.4).to(10,0.4)
    L2 = Linear().at(12,4).to(20,40)
    B1 = Bezier().connect(L1,L2)
    x,y = B1.get_coordinates()
