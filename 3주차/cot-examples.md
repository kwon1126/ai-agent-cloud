# Chain-of-Thought (CoT) Prompting 예제

## 1. 일반 (No CoT)

> 리스트에서 가장 큰 값을 찾는 코드를 작성하라.

---

## 2. Zero-Shot CoT

> 리스트에서 가장 큰 값을 찾는 코드를 작성하라.
>
> **Let's think step-by-step.**

---

## 3. Multi-Shot CoT

> 다음 문제를 단계적으로 생각해서 Python 코드로 작성하세요.
>
> ### Example 1
>
> **문제:** 리스트의 합을 구하는 함수를 작성하라.
>
> **생각:**
> - 리스트의 각 숫자를 반복하면서 더해야 한다.
> - for 문을 사용하면 된다.
>
> **코드:**
> ```python
> def sum_list(nums):
>     total = 0
>     for n in nums:
>         total += n
>     return total
> ```
>
> ### Example 2
>
> **문제:** 리스트에서 짝수만 출력하는 코드를 작성하라.
>
> **생각:**
> - 리스트를 반복하면서
> - 숫자가 2로 나누어 떨어지는지 확인한다.
>
> **코드:**
> ```python
> numbers = [1, 2, 3, 4]
> for n in numbers:
>     if n % 2 == 0:
>         print(n)
> ```
>
> ### 문제
>
> 리스트에서 가장 큰 값을 찾는 코드를 작성하라.
