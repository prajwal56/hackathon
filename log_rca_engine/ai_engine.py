
import json
import os
import numpy as np
from openai import OpenAI
from typing import List
from sklearn.metrics.pairwise import cosine_similarity

class AIEngine:
    def __init__(self, config):
        self.config = config
        self.api_key = config['api_key']
        self.client = OpenAI(api_key=self.api_key)
        self.model = config['model']

    def generate_prompt(self, logs: str):
        try:
            prompt = logs
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You get the RCA for the error logs. get the solution for it in json format. output format {'rca':'rca of the error','solution':'solution of the error'} in json"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500,
            )
            raw_output = response.choices[0].message.content.strip()
            try:
                try:
                    return json.loads(raw_output)
                except:
                    return eval(raw_output)
            except json.JSONDecodeError:
                return {"error": "Output is not valid JSON", "raw": raw_output}
        except Exception as e:
            return {"error": str(e)}
