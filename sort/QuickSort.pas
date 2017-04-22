const n=200;
var x:array[1..n] of integer;
    i:integer;
procedure sort(l,r:integer); {l-левый конец масива,r-правый конец}
var
  i,j,x1,y1,m: integer;
begin
  i:=l;
  j:=r;
  m:=round ((l+r)/2); {средний элемент}
  x1:=x[m];
  repeat
    while x[i]<x1 do inc(i); {пока левый больше среднего, подвигоем левый край вправо }
    while x[j]>x1 do dec(j); {пока правый меньше среднего, подвигаем левый вправо}
    if i<=j then {если левый и правый срослись}
     begin
      y1:=x[i];
      x[i]:=x[j]; {меняем левый и правый}
      x[j]:=y1;
      inc(i); {левый вправо}
      dec(j); {правый влево}
     end;
  until i>j; {конец одной перестановки}
  if l<j then sort(l,j); {рекурсивно сортируем}
  if i<r then sort(i,r); {или левую или правую части}
end;
 
begin
clrscr;
randomize;
writeln('Исходный массив:');
for i:=1 to n do
  begin
   x[i]:=random(1000);
   write(x[i]:4);
  end;
writeln;
sort(1,n);
writeln('Массив после сортировки: ');
for i:=1 to n do
write(x[i]:4);
end.