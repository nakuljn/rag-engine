import gradio as gr
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from api_client import api_client
import logging

logger = logging.getLogger(__name__)

# Custom CSS for clean white UI with small fonts
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif !important;
    font-size: 12px !important;
}

.gr-button {
    font-size: 12px !important;
    padding: 6px 12px !important;
    border-radius: 4px !important;
}

.gr-textbox {
    font-size: 12px !important;
}

.gr-dropdown {
    font-size: 12px !important;
}

.gr-dataframe {
    font-size: 11px !important;
}

.gr-tab {
    font-size: 12px !important;
}

.gr-form {
    background: white !important;
}

.gr-panel {
    background: white !important;
    border: 1px solid #e0e0e0 !important;
}
"""

class RAGGradioUI:
    def __init__(self):
        self.current_files = []
        self.current_collections = []
        self.chat_history = []

    # Utility functions
    def _format_response(self, response: Dict[str, Any]) -> str:
        if response["success"]:
            data = response.get("data", {})
            message = data.get("message", "Success")
            return f"✅ {message}"
        else:
            return f"❌ {response['error']}"

    def _update_file_list(self) -> pd.DataFrame:
        response = api_client.list_files()
        if response["success"]:
            files_data = response["data"].get("body", {}).get("files", [])
            self.current_files = files_data

            if files_data:
                df = pd.DataFrame(files_data)
                # Reorder columns for better display
                df = df[["filename", "file_size", "upload_date", "file_id"]]
                df["file_size"] = df["file_size"].apply(lambda x: f"{x:,} bytes")
                df["upload_date"] = pd.to_datetime(df["upload_date"]).dt.strftime("%Y-%m-%d %H:%M")
                return df
            else:
                return pd.DataFrame({"Message": ["No files uploaded yet"]})
        else:
            return pd.DataFrame({"Error": [response["error"]]})

    def _update_collection_list(self) -> pd.DataFrame:
        response = api_client.list_collections()
        if response["success"]:
            collections_data = response["data"].get("body", {}).get("collections", [])
            self.current_collections = collections_data

            if collections_data:
                df = pd.DataFrame({"Collection Name": collections_data})
                return df
            else:
                return pd.DataFrame({"Message": ["No collections created yet"]})
        else:
            return pd.DataFrame({"Error": [response["error"]]})

    def _get_file_choices(self) -> List[str]:
        if self.current_files:
            return [f"{file['filename']} ({file['file_id'][:8]}...)" for file in self.current_files]
        return ["No files available"]

    def _get_file_id_from_choice(self, choice: str) -> Optional[str]:
        if not choice or choice == "No files available":
            return None

        for file in self.current_files:
            if choice.startswith(file['filename']):
                return file['file_id']
        return None

    def _get_collection_choices(self) -> List[str]:
        if self.current_collections:
            return self.current_collections
        return ["No collections available"]

    def _get_collection_from_choice(self, choice: str) -> Optional[str]:
        if not choice or choice == "No collections available":
            return None
        return choice

    def upload_file(self, file) -> Tuple[str, pd.DataFrame, gr.Dropdown, gr.Dropdown]:
        if file is None:
            return "⚠️ Please select a file to upload", self._update_file_list(), gr.Dropdown(choices=self._get_file_choices()), gr.Dropdown(choices=self._get_file_choices())

        try:
            file_content = file.read() if hasattr(file, 'read') else open(file.name, 'rb').read()
            filename = file.name.split('/')[-1] if hasattr(file, 'name') else 'uploaded_file'
            response = api_client.upload_file(file_content, filename)

            updated_df = self._update_file_list()
            updated_choices = self._get_file_choices()

            return self._format_response(response), updated_df, gr.Dropdown(choices=updated_choices, value=None), gr.Dropdown(choices=updated_choices, value=None)

        except Exception as e:
            logger.error(f"File upload error: {e}")
            choices = self._get_file_choices()
            return f"❌ Upload failed: {str(e)}", self._update_file_list(), gr.Dropdown(choices=choices), gr.Dropdown(choices=choices)


    def delete_file(self, file_choice: str) -> Tuple[str, pd.DataFrame, gr.Dropdown, gr.Dropdown]:
        file_id = self._get_file_id_from_choice(file_choice)

        if not file_id:
            choices = self._get_file_choices()
            return "⚠️ Please select a file to delete", self._update_file_list(), gr.Dropdown(choices=choices), gr.Dropdown(choices=choices)

        response = api_client.delete_file(file_id)

        updated_df = self._update_file_list()
        updated_choices = self._get_file_choices()

        return self._format_response(response), updated_df, gr.Dropdown(choices=updated_choices, value=None), gr.Dropdown(choices=updated_choices, value=None)


    def refresh_files(self) -> Tuple[pd.DataFrame, gr.Dropdown]:
        updated_df = self._update_file_list()
        updated_choices = self._get_file_choices()
        return updated_df, gr.Dropdown(choices=updated_choices, value=None)

    def refresh_collections(self) -> Tuple[pd.DataFrame, gr.Dropdown, gr.Dropdown]:
        updated_df = self._update_collection_list()
        updated_choices = self._get_collection_choices()
        return (updated_df,
                gr.Dropdown(choices=updated_choices, value=None),
                gr.Dropdown(choices=updated_choices, value=None))

    def create_collection(self, collection_name: str) -> Tuple[str, pd.DataFrame, gr.Dropdown, gr.Dropdown]:
        if not collection_name.strip():
            choices = self._get_collection_choices()
            return ("⚠️ Please enter a collection name", self._update_collection_list(),
                    gr.Dropdown(choices=choices), gr.Dropdown(choices=choices))

        response = api_client.create_collection(collection_name.strip())
        updated_df = self._update_collection_list()
        updated_choices = self._get_collection_choices()

        return (self._format_response(response), updated_df,
                gr.Dropdown(choices=updated_choices, value=None),
                gr.Dropdown(choices=updated_choices, value=None))

    def link_content(self, collection_choice: str, file_choice: str) -> str:
        collection_name = self._get_collection_from_choice(collection_choice)
        if not collection_name:
            return "⚠️ Please select a collection"

        file_id = self._get_file_id_from_choice(file_choice)
        if not file_id:
            return "⚠️ Please select a file to link"

        # Find the file details from current_files
        selected_file = None
        for file in self.current_files:
            if file['file_id'] == file_id:
                selected_file = file
                break

        if not selected_file:
            return "⚠️ File not found in current files list"

        # Create the new API format - array of file objects
        files_to_link = [{
            "name": selected_file['filename'],
            "id": file_id,
            "field": "text"  # Default field type
        }]

        response = api_client.link_content(collection_name, files_to_link)

        # Handle 207 multi-status response
        if response["success"] and response["status_code"] == 207:
            results = response.get("data", [])
            if results:
                result = results[0]  # Get first (and only) result
                status_code = result.get("status_code", 500)
                indexing_status = result.get("indexing_status", "UNKNOWN")
                message = result.get("message", "No message")

                if status_code == 200:
                    return f"✅ {indexing_status}: {message}"
                else:
                    return f"❌ {indexing_status}: {message}"
            else:
                return "❌ No response data received"
        else:
            return self._format_response(response)

    def query_collection(self, collection_choice: str, query: str) -> str:
        collection_name = self._get_collection_from_choice(collection_choice)
        if not collection_name:
            return "⚠️ Please select a collection"

        if not query.strip():
            return "⚠️ Please enter a search query"

        response = api_client.query_collection(collection_name, query.strip())

        if response["success"]:
            data = response.get("data", {})
            answer = data.get("answer", "No answer")
            confidence = data.get("confidence", 0.0)
            is_relevant = data.get("is_relevant", False)
            chunks = data.get("chunks", [])

            result = f"**Answer:** {answer}\n"
            result += f"**Confidence:** {confidence:.2f}\n"
            result += f"**Relevant:** {'Yes' if is_relevant else 'No'}\n"
            if chunks:
                result += f"**Sources:** {len(chunks)} document(s)"

            return result
        else:
            return self._format_response(response)

    def chat_with_collection(self, collection_choice: str, message: str, history: List) -> Tuple[List, str]:
        if history is None:
            history = []

        if not message.strip():
            return history, ""

        collection_name = self._get_collection_from_choice(collection_choice)
        if not collection_name:
            history.append(["❌ Please select a collection first", ""])
            return history, ""

        history.append([message, ""])

        response = api_client.query_collection(collection_name, message.strip())

        if response["success"]:
            data = response.get("data", {})
            answer = data.get("answer", "No answer")
            history[-1][1] = answer
        else:
            history[-1][1] = f"❌ {response.get('error', 'Unknown error')}"

        return history, ""

    def clear_chat(self) -> List:
        return []

    def create_interface(self) -> gr.Blocks:
        with gr.Blocks(css=custom_css, title="RAG Engine", theme=gr.themes.Default()) as demo:
            gr.Markdown("# 🚀 RAG Engine", elem_classes=["center"])
            gr.Markdown("Upload files, create collections, and query your documents", elem_classes=["center"])

            with gr.Tabs():
                # Tab 1: File Management
                with gr.Tab("📁 File Management"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("### Upload Files")
                            file_upload = gr.File(
                                label="Select File",
                                file_types=None,
                                elem_classes=["file-upload"]
                            )
                            upload_btn = gr.Button("Upload", variant="primary", size="sm")
                            upload_status = gr.Textbox(
                                label="Status",
                                interactive=False,
                                lines=2,
                                placeholder="Ready to upload files..."
                            )

                        with gr.Column(scale=2):
                            gr.Markdown("### Manage Files")
                            refresh_files_btn = gr.Button("🔄 Refresh Files", size="sm")
                            files_table = gr.Dataframe(
                                headers=["Filename", "Size", "Upload Date", "File ID"],
                                interactive=False,
                                wrap=True
                            )

                            with gr.Row():
                                file_selector = gr.Dropdown(
                                    label="Select File to Delete",
                                    choices=[],
                                    interactive=True
                                )
                                delete_btn = gr.Button("🗑️ Delete", variant="stop", size="sm")

                # Tab 2: Collection Management
                with gr.Tab("📚 Collection Management"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("### Create Collection")
                            collection_name = gr.Textbox(
                                label="Collection Name",
                                placeholder="Enter collection name...",
                                lines=1
                            )
                            create_collection_btn = gr.Button("Create Collection", variant="primary", size="sm")
                            collection_status = gr.Textbox(
                                label="Status",
                                interactive=False,
                                lines=2,
                                placeholder="Ready to create collections..."
                            )

                        with gr.Column(scale=2):
                            gr.Markdown("### Collection Operations")
                            refresh_collections_btn = gr.Button("🔄 Refresh Collections", size="sm")
                            collections_table = gr.Dataframe(
                                headers=["Collection Info"],
                                interactive=False,
                                wrap=True
                            )

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### Link Content")
                            link_collection_dropdown = gr.Dropdown(
                                label="Select Collection",
                                choices=[],
                                interactive=True
                            )
                            link_file_selector = gr.Dropdown(
                                label="Select File to Link",
                                choices=[],
                                interactive=True
                            )
                            link_btn = gr.Button("🔗 Link Content", variant="secondary", size="sm")
                            link_status = gr.Textbox(label="Link Status", interactive=False, lines=1)

                # Tab 3: Chatbot
                with gr.Tab("💬 Chatbot"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### RAG-based Chat")
                            chat_collection_dropdown = gr.Dropdown(
                                label="Select Collection",
                                choices=[],
                                interactive=True
                            )

                    with gr.Row():
                        chatbot = gr.Chatbot(
                            label="Chat with your documents",
                            height=400,
                            show_label=True,
                            value=[]
                        )

                    with gr.Row():
                        with gr.Column(scale=4):
                            chat_input = gr.Textbox(
                                label="Message",
                                placeholder="Ask a question about your documents...",
                                lines=1,
                                max_lines=3
                            )
                        with gr.Column(scale=1):
                            chat_send_btn = gr.Button("Send", variant="primary", size="sm")
                            clear_chat_btn = gr.Button("Clear Chat", variant="secondary", size="sm")

            # Event handlers for File Management
            upload_btn.click(
                fn=self.upload_file,
                inputs=[file_upload],
                outputs=[upload_status, files_table, file_selector, link_file_selector],
                queue=False
            )

            delete_btn.click(
                fn=self.delete_file,
                inputs=[file_selector],
                outputs=[upload_status, files_table, file_selector, link_file_selector],
                queue=False
            )

            refresh_files_btn.click(
                fn=self.refresh_files,
                outputs=[files_table, file_selector],
                queue=False
            )

            create_collection_btn.click(
                fn=self.create_collection,
                inputs=[collection_name],
                outputs=[collection_status, collections_table, link_collection_dropdown, chat_collection_dropdown],
                queue=False
            )

            link_btn.click(
                fn=self.link_content,
                inputs=[link_collection_dropdown, link_file_selector],
                outputs=[link_status],
                queue=False
            )

            refresh_collections_btn.click(
                fn=self.refresh_collections,
                outputs=[collections_table, link_collection_dropdown, chat_collection_dropdown],
                queue=False
            )

            chat_send_btn.click(
                fn=self.chat_with_collection,
                inputs=[chat_collection_dropdown, chat_input],
                outputs=[chatbot, chat_input],
                queue=False
            )

            chat_input.submit(
                fn=self.chat_with_collection,
                inputs=[chat_collection_dropdown, chat_input],
                outputs=[chatbot, chat_input],
                queue=False
            )

            clear_chat_btn.click(
                fn=self.clear_chat,
                outputs=[chatbot],
                queue=False
            )

            # Initialize with current data on load
            def initialize_data():
                files_df, file_choices = self.refresh_files()
                collections_df, link_dropdown, chat_dropdown = self.refresh_collections()
                return (files_df, file_choices, collections_df,
                        gr.Dropdown(choices=self._get_file_choices()),
                        link_dropdown, chat_dropdown)

            demo.load(
                fn=initialize_data,
                outputs=[files_table, file_selector, collections_table, link_file_selector,
                        link_collection_dropdown, chat_collection_dropdown],
                queue=False
            )

        return demo