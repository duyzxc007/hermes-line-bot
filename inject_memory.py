from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DB_DIR = "./chroma_db"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_store = Chroma(embedding_function=embeddings, persist_directory=DB_DIR)

chunks = [
    "[บันทึกโดย ดุ๊ย]: อัปเดตข้อมูล Identity & Professional Role - เป็น Project Engineer แบบ Hybrid (ลุยหน้างาน + บริหารโครงการ) สไตล์ทํางาน Reactive + Analytical Worker ชอบแก้ปัญหาเฉพาะหน้า ไม่ชอบ Routine ล้วนๆ ระดับการตัดสินใจแบบ Engineer-style เน้น Practicality ใช้งานได้จริงภายใต้ข้อจำกัด",
    
    "[บันทึกโดย ดุ๊ย]: อัปเดตข้อมูล Technical Expertise - เชี่ยวชาญระบบไฟฟ้า โทรคมนาคม (RF/Radio) และ GPS/GNSS ยึดมาตรฐาน IEC, IEEE, ISO, NEC ทักษะด้าน IT: เขียน Python, Docker, Cisco Nexus, Catalyst 9000, Web App (Firebase+Vite ทำแอปหุ้น) Project สำคัญ: ติดตั้งสถานีตรวจสอบคลื่นในใต้ 10 ไซต์ (ทำกับพี่ถึก และ พี่ X), ออกแบบ GPS อาคาร 9 ชั้น (สาย Riser 36ม.) เครื่องมือโปร: Milwaukee, Snap-on, PB Swiss",
    
    "[บันทึกโดย ดุ๊ย]: อัปเดตข้อมูล Financial, Growth & Learning - เป็นนักลงทุน Value Investing เน้น Growth หาของดีราคาถูก วิเคราะห์งบลงทุนใน BDMS, PR9, BH และ GE Aerospace. การเรียนรู้แบบ Applied Learning ใช้ทันที ไม่วิชาการจ๋า ชอบนำของยากมาทำ Framework. เตรียมตัวสอบ ก.พ. แบบ 5 วันเน้นกฎหมาย/ตรรกศาสตร์",
    
    "[บันทึกโดย ดุ๊ย]: อัปเดตข้อมูล Lifestyle, Grooming & Gaming - มีแฟนชื่อ น้องมายด์ มีแมวชื่อ ผักชี (เคยทำ ID Card ให้) ละเอียดอ่อนเรื่องอวยพรแม่แฟน. สกินแคร์: ขับเคลื่อนด้วยข้อมูล เน้น Barrier Repair (Ceramides, Vit B5, Rice extract) และยาสีฟัน PFAS-free. น้ำหอม: โทน Masculine/Metallic/Woody (Chanel Platinum, Terre d'Hermes, Armaf, Afnan). เกม: Tactical Extraction (Delta Force, Arena Breakout), Auto Chess (TFT), Co-op (Once Human, Ragnarok)",
    
    "[บันทึกโดย ดุ๊ย]: อัปเดตข้อมูล Inner Drivers & Blind Spots - แรงขับเคลื่อนคือ Mastery (เก่งจริง), Control (เข้าถึงโครงสร้างรับความเสี่ยงได้), Efficiency (ลด waste แบบ manual), Progress จุดระวัง (Blind Spots): Over-optimization อาจเสียเวลามากไป, Expectation Gap คาดหวังคนอื่นมีตรรกะเหมือนกันจนหงุดหงิด, Under-communication ประมวลผลไวไปจนข้ามการอธิบายให้ฝั่ง Non-tech",
    
    "[บันทึกโดย ดุ๊ย]: อัปเดตข้อมูล AI Collaboration Profile - โทนการสื่อสารที่ต้องการจาก AI: Professional + เป็นกันเองแบบ Senior Engineer (No fluff, แทรกตลกได้นิดหน่อย) รูปแบบคำตอบ: ต้องมี Executive Summary นำก่อนเสมอ ตอบแบบ Decision-ready (เสนอ Option+Recommendation+Trade-off) ใช้ Framework, Checklist หรือ Excel-style ถ้ายากไป กฎเหล็ก: ถ้าไม่แน่ใจต้องตอบว่า 'ไม่แน่ใจ' พร้อมเสนอวิธีเช็กความถูกต้อง"
]

vector_store.add_texts(
    texts=chunks,
    metadatas=[{"name": "ดุ๊ย", "user_id": "system_injected_updated"}] * len(chunks)
)
print("SUCCESS: Advanced Dossier Memory Injected to ChromaDB")
