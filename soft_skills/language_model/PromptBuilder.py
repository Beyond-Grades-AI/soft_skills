def create_questions_prompt(topic, points, num_questions=10):
    questions_prompt = f"עבור הנושא הבא: \n" \
                       f"{topic}\n" \
                       f"כתוב שאלות על הנושא בצורה הבאה: \n" \
                       f"כתוב {num_questions} שאלות\n" \
                       f"השאלות צריכות להיות כתובות בעברית.\n" \
                       f"תשתמש בנקודות הבאות כדי לקבל כיוון לכתיבת השאלות:\n" \
                       f"{points} \n" \
                       f"השאלות צריכות להיות מתאימות לילדים בחטיבת ביניים\n" \
                       f"כאשר אתה בונה את השאלות תנסה לדבר ע לכמה שיותר דמויות"
    return questions_prompt


def create_empathy_eval_prompt(question_text, answer, empathy_points):
    empathy_evl_prompt = f"עבור השאלה הבאה:\n" \
                         f"{question_text}\n" \
                         f"יש לי את התשובה הבאה:\n" \
                         f"{answer}\n" \
                         f"תנתח את התשובה לפי הנקודות הבאות לתשובה אחת, בנוסף תתחיל את התשובה בכן אם הטקסט מראה על אמפתיה ולמה, או תתחיל את התשובה בלא אם אין אמפתיה בטקסט ולמה, אם אין מגבלת טקסט אל תוסיף את זה לתשובה, אם בתשובה הנתונה אין שאלה המעמיקה את ההבנה אל תוסיף את זה לתשובה: \n" \
                         f"{empathy_points}\n"\
                         f"התשובה צריכה להיות כתובה בפסקה אחת ולא מפורטת לפי נקודות\n" \
                         f"אם התשובה לא עונה על השאלה, תחזיר לא ניתן לתת הערכה על תשובה זו"
    return empathy_evl_prompt


def create_critical_thinking_eval_prompt(question_text, answer, critical_thinking_points):
    critical_thinking_eval_prompt = f"להלן שאלה ותשובה. נתח את הטקסט הבא והחלט אם הוא מביעה חשיבה ביקורתית או לא, ביחס לשאלה שהוצגה:\n" \
                                    f"השאלה:\n" \
                                    f"{question_text}\n" \
                                    f"התשובה:\n" \
                                    f"{answer}\n" \
                                    f"מרכיבי חשיבה ביקורתית:\n" \
                                    f"{critical_thinking_points}\n" \
                                    f"התשובה שלך בעברית תתחיל בכן אם התשובה מביעה חשיבה ביקורתית ביחס לשאלה, ואחר כך תפרט רק את המרכיבים הרלוונטיים שבאים לידי ביטוי, תוך הדגמה מהתשובה. אם לא, התשובה תתחיל בלא והיא תסביר בעברית מדוע התשובה אינה מבטאת חשיבה ביקורתית ביחס לשאלה.\n"\
                                    f"התשובה צריכה להיות כתובה בפסקה אחת ולא מפורטת לפי נקודות\n" \
                                    f"אם התשובה לא עונה על השאלה, תחזיר לא ניתן לתת הערכה על תשובה זו"
    return critical_thinking_eval_prompt
