# Prompting 기법 예제

## 1. K-Shot Prompting (For문 작성)

### Zero-Shot

> 다음 리스트를 출력하는 Python for문을 작성하세요.
>
> `fruits = ["apple", "banana", "orange"]`

---

### 1-Shot

> 다음 예제를 참고해서 Python for문을 작성하세요.
>
> **Example:**
> ```python
> numbers = [1, 2, 3]
> for n in numbers:
>     print(n)
> ```
>
> **문제:**
> `fruits = ["apple", "banana", "orange"]`

---

### 3-Shot

> 다음 예제를 참고하세요.
>
> **Example 1:**
> ```python
> numbers = [1, 2, 3]
> for n in numbers:
>     print(n)
> ```
>
> **Example 2:**
> ```python
> animals = ["dog", "cat"]
> for a in animals:
>     print(a)
> ```
>
> **Example 3:**
> ```python
> colors = ["red", "blue"]
> for c in colors:
>     print(c)
> ```
>
> **문제:**
> `fruits = ["apple", "banana", "orange"]`

---

## 2. 감정 분석 (Zero-Shot vs Few-Shot)

### Zero-Shot

> 다음 문장의 감정을 분석하세요.
>
> "와 진짜 대박이다.."

---

### Few-Shot

> 다음 문장의 감정을 분석하세요.
>
> **Example:**
> | 문장 | 감정 |
> |------|------|
> | "와 진짜 대박이다" | 긍정 |
> | "와 진짜 대박이다..." | 부정 |
> | "와 진짜 대박이다 ㅋㅋ" | 긍정 |
>
> **문장:**
> "와 진짜 대박이다.."
