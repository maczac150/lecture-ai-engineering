# batch_service.py
from collections import deque
import threading
import time
import uuid
import traceback

class BatchProcessor:
    """
    バッチ処理を行うクラス
    複数のリクエストをキューに蓄積し、一定数または一定時間ごとにバッチ処理する
    """
    def __init__(self, model, batch_size=5, max_wait_time=2.0):
        self.queue = deque()
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.model = model
        self.lock = threading.Lock()
        self.processing = False
        self.results = {}
        self.last_process_time = time.time()
        self._start_processing_thread()
    
    def _start_processing_thread(self):
        """バッチ処理用のスレッドを開始する"""
        thread = threading.Thread(target=self._process_queue_periodically)
        thread.daemon = True
        thread.start()
        print("バッチ処理スレッドを開始しました")
    
    def add_request(self, prompt, params=None):
        """
        リクエストをキューに追加する
        
        Args:
            prompt: 生成するテキストのプロンプト
            params: 生成パラメータ (temperature, top_p など)
            
        Returns:
            request_id: リクエストを識別するためのID
        """
        request_id = str(uuid.uuid4())
        with self.lock:
            self.queue.append((request_id, prompt, params or {}))
            print(f"リクエストをキューに追加しました (ID: {request_id}, キューサイズ: {len(self.queue)})")
        return request_id
    
    def get_result(self, request_id, wait=True, timeout=10.0):
        """
        リクエストの結果を取得する
        
        Args:
            request_id: リクエストID
            wait: 結果が出るまで待つかどうか
            timeout: 最大待機時間（秒）
            
        Returns:
            result: 生成結果、またはNone（タイムアウト時）
        """
        start_time = time.time()
        while wait and (time.time() - start_time) < timeout:
            if request_id in self.results:
                result = self.results.pop(request_id)
                print(f"リクエスト {request_id} の結果を返却します")
                return result
            time.sleep(0.1)
        
        # タイムアウトまたは待機しない場合
        if request_id in self.results:
            result = self.results.pop(request_id)
            return result
        
        print(f"リクエスト {request_id} の結果が見つかりませんでした")
        return None
    
    def _process_queue_periodically(self):
        """定期的にキューを処理するループ"""
        while True:
            current_time = time.time()
            time_since_last_process = current_time - self.last_process_time
            
            # バッチサイズに達したか、最大待機時間を超えた場合に処理
            with self.lock:
                should_process = (
                    len(self.queue) >= self.batch_size or 
                    (len(self.queue) > 0 and time_since_last_process >= self.max_wait_time)
                )
            
            if should_process:
                self._process_batch()
                self.last_process_time = time.time()
            
            time.sleep(0.1)  # スリープして CPU 使用率を下げる
    
    def _process_batch(self):
        """キューからバッチを取り出して処理する"""
        with self.lock:
            if not self.queue or self.processing:
                return
            
            current_batch = []
            current_ids = []
            
            # バッチサイズまでリクエストを取り出す
            while self.queue and len(current_batch) < self.batch_size:
                request_id, prompt, params = self.queue.popleft()
                current_batch.append((prompt, params))
                current_ids.append(request_id)
            
            if not current_batch:
                return
                
            self.processing = True
            print(f"バッチ処理を開始します (サイズ: {len(current_batch)})")
        
        try:
            # バッチ処理の実行
            prompts = [item[0] for item in current_batch]
            all_params = [item[1] for item in current_batch]
            
            # モデルでバッチ推論を実行
            batch_results = self._batch_inference(prompts, all_params)
            
            # 結果を保存
            for i, request_id in enumerate(current_ids):
                if i < len(batch_results):
                    self.results[request_id] = batch_results[i]
                else:
                    self.results[request_id] = {"error": "バッチ処理中にエラーが発生しました"}
            
            print(f"バッチ処理が完了しました (サイズ: {len(current_batch)})")
                
        except Exception as e:
            print(f"バッチ処理中にエラーが発生しました: {e}")
            traceback.print_exc()
            
            # エラー時は全てのリクエストにエラーを返す
            for request_id in current_ids:
                self.results[request_id] = {"error": f"バッチ処理中にエラーが発生しました: {str(e)}"}
        
        finally:
            self.processing = False
    
    def _batch_inference(self, prompts, all_params):
        """
        バッチ推論を実行する
        
        Args:
            prompts: プロンプトのリスト
            all_params: 各プロンプトのパラメータのリスト
            
        Returns:
            results: 生成結果のリスト
        """
        results = []
        
        # 現在の実装では、バッチ処理を模倣するために個別に処理
        # 将来的には、モデルがネイティブバッチ処理をサポートする場合は変更する
        for i, prompt in enumerate(prompts):
            params = all_params[i]
            try:
                # 個別のパラメータを適用
                output = self.model(
                    prompt, 
                    max_new_tokens=params.get('max_new_tokens', 512),
                    do_sample=params.get('do_sample', True),
                    temperature=params.get('temperature', 0.7),
                    top_p=params.get('top_p', 0.9)
                )
                results.append(output)
            except Exception as e:
                print(f"推論中にエラーが発生しました (プロンプト {i}): {e}")
                results.append({"error": f"推論エラー: {str(e)}"})
        
        return results

    def get_queue_size(self):
        """現在のキューサイズを取得する"""
        with self.lock:
            return len(self.queue)
    
    def get_processing_status(self):
        """処理状態を取得する"""
        return {
            "queue_size": self.get_queue_size(),
            "processing": self.processing,
            "results_waiting": len(self.results)
        }
