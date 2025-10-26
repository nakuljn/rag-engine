import gradio as gr
import pandas as pd
import json
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

    def _format_structured_response(self, response_data: Dict[str, Any]) -> str:
        formatted_json = json.dumps(response_data, indent=2, ensure_ascii=False)
        return f"```json\n{formatted_json}\n```"

    def _get_file_ids_from_choices(self, choices: List[str]) -> List[str]:
        file_ids = []
        for choice in choices:
            if not choice or choice == "No files available":
                continue
            for file in self.current_files:
                if choice.startswith(file['filename']):
                    file_ids.append(file['file_id'])
                    break
        return file_ids

    def _format_multi_operation_response(self, responses: List[Dict], operation: str) -> str:
        if not responses:
            return f"❌ No {operation} operations performed"

        success_count = sum(1 for r in responses if r.get("status_code") == 200)
        total_count = len(responses)
        failed_count = total_count - success_count

        if failed_count == 0:
            return f"✅ {success_count} file(s) {operation}ed successfully"
        elif success_count == 0:
            return f"❌ All {total_count} file(s) failed to {operation}"
        else:
            return f"⚠️ {success_count} {operation}ed, {failed_count} failed"

    def _translate_error_message(self, backend_message: str, operation: str) -> str:
        # Mapping backend errors to user-friendly messages
        error_mappings = {
            # Link operation errors
            "File not found": "File missing",
            "File already linked, unlink first": "Already linked",
            "Could not read file content": "File unreadable",
            "Failed to generate embedding": "Processing failed",
            "Failed to link content to collection": "Database error",

            # Unlink operation errors
            "File not found in collection": "Not linked",
            "Failed to unlink content from collection": "Database error",
        }

        # Check for exact matches first
        if backend_message in error_mappings:
            return error_mappings[backend_message]

        # Check for partial matches (for "Internal error: ..." messages)
        if backend_message.startswith("Internal error:"):
            return "System error"

        # Default fallback
        return "Operation failed"

    def _format_file_status_list(self, responses: List[Dict], operation: str) -> str:
        if not responses:
            return f"❌ No {operation} operations performed"

        status_lines = []
        for response in responses:
            filename = response.get("name", "unknown_file")
            status_code = response.get("status_code", 500)

            if status_code == 200:
                if operation == "link":
                    status_lines.append(f"{filename} ✅ LINKED")
                else:  # unlink
                    status_lines.append(f"{filename} ❌ UNLINKED")
            else:
                backend_message = response.get("message", "Failed")
                user_friendly_message = self._translate_error_message(backend_message, operation)
                status_lines.append(f"{filename} ❌ {user_friendly_message.upper()}")

        return "\n".join(status_lines)

    def upload_file(self, file) -> Tuple[str, pd.DataFrame, gr.Dropdown, gr.Dropdown]:
        if file is None:
            return "⚠️ Please select a file to upload", self._update_file_list(), gr.Dropdown(choices=self._get_file_choices()), gr.Dropdown(choices=self._get_file_choices())

        try:
            file_content = file.read() if hasattr(file, 'read') else open(file.name, 'rb').read()
            filename = file.name.split('/')[-1] if hasattr(file, 'name') else 'uploaded_file'
            response = api_client.upload_file(file_content, filename)

            updated_df = self._update_file_list()
            updated_choices = self._get_file_choices()

            return self._format_response(response), updated_df, gr.Dropdown(choices=updated_choices, value=None), gr.Dropdown(choices=updated_choices, value=None, multiselect=True)

        except Exception as e:
            logger.error(f"File upload error: {e}")
            choices = self._get_file_choices()
            return f"❌ Upload failed: {str(e)}", self._update_file_list(), gr.Dropdown(choices=choices), gr.Dropdown(choices=choices, multiselect=True)


    def delete_file(self, file_choice: str) -> Tuple[str, pd.DataFrame, gr.Dropdown, gr.Dropdown]:
        file_id = self._get_file_id_from_choice(file_choice)

        if not file_id:
            choices = self._get_file_choices()
            return "⚠️ Please select a file to delete", self._update_file_list(), gr.Dropdown(choices=choices), gr.Dropdown(choices=choices, multiselect=True)

        response = api_client.delete_file(file_id)

        updated_df = self._update_file_list()
        updated_choices = self._get_file_choices()

        return self._format_response(response), updated_df, gr.Dropdown(choices=updated_choices, value=None), gr.Dropdown(choices=updated_choices, value=None, multiselect=True)


    def refresh_files(self) -> Tuple[pd.DataFrame, gr.Dropdown]:
        updated_df = self._update_file_list()
        updated_choices = self._get_file_choices()
        return updated_df, gr.Dropdown(choices=updated_choices, value=None)

    def refresh_collections(self) -> Tuple[pd.DataFrame, gr.Dropdown, gr.Dropdown, gr.Dropdown]:
        updated_df = self._update_collection_list()
        updated_choices = self._get_collection_choices()
        return (updated_df,
                gr.Dropdown(choices=updated_choices, value=None),
                gr.Dropdown(choices=updated_choices, value=None),
                gr.Dropdown(choices=updated_choices, value=None))

    def create_collection(self, collection_name: str) -> Tuple[str, pd.DataFrame, gr.Dropdown, gr.Dropdown, gr.Dropdown]:
        if not collection_name.strip():
            choices = self._get_collection_choices()
            return ("⚠️ Please enter a collection name", self._update_collection_list(),
                    gr.Dropdown(choices=choices), gr.Dropdown(choices=choices), gr.Dropdown(choices=choices))

        response = api_client.create_collection(collection_name.strip())
        updated_df = self._update_collection_list()
        updated_choices = self._get_collection_choices()

        return (self._format_response(response), updated_df,
                gr.Dropdown(choices=updated_choices, value=None),
                gr.Dropdown(choices=updated_choices, value=None),
                gr.Dropdown(choices=updated_choices, value=None))

    def link_content(self, collection_choice: str, file_choices: List[str]) -> str:
        collection_name = self._get_collection_from_choice(collection_choice)
        if not collection_name:
            return "⚠️ Please select a collection"

        if not file_choices:
            return "⚠️ Please select files to link"

        file_ids = self._get_file_ids_from_choices(file_choices)
        if not file_ids:
            return "⚠️ Selected files not found"

        # Create files array for API
        files_to_link = []
        for file_id in file_ids:
            # Find the file details from current_files
            selected_file = None
            for file in self.current_files:
                if file['file_id'] == file_id:
                    selected_file = file
                    break

            if selected_file:
                files_to_link.append({
                    "name": selected_file['filename'],
                    "file_id": file_id,
                    "type": "text"
                })

        if not files_to_link:
            return "⚠️ No valid files to link"

        response = api_client.link_content(collection_name, files_to_link)

        # Handle 207 multi-status response
        if response["success"] and response["status_code"] == 207:
            results = response.get("data", [])
            return self._format_file_status_list(results, "link")
        else:
            return self._format_response(response)

    def unlink_content(self, collection_choice: str, file_choices: List[str]) -> str:
        collection_name = self._get_collection_from_choice(collection_choice)
        if not collection_name:
            return "⚠️ Please select a collection"

        if not file_choices:
            return "⚠️ Please select files to unlink"

        file_ids = self._get_file_ids_from_choices(file_choices)
        if not file_ids:
            return "⚠️ Selected files not found"

        response = api_client.unlink_content(collection_name, file_ids)

        # Handle 207 multi-status response
        if response["success"] and response["status_code"] == 207:
            results = response.get("data", [])
            return self._format_file_status_list(results, "unlink")
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

    def chat_with_collection(self, collection_choice: str, message: str, history: List, structured_output: bool = False, enable_critic: bool = True) -> Tuple[List, str]:
        if history is None:
            history = []

        if not message.strip():
            return history, ""

        collection_name = self._get_collection_from_choice(collection_choice)
        if not collection_name:
            history.append(["❌ Please select a collection first", ""])
            return history, ""

        history.append([message, ""])

        # Auto-disable critic if structured output is OFF
        actual_enable_critic = enable_critic and structured_output

        response = api_client.query_collection(collection_name, message.strip(), actual_enable_critic)

        if response["success"]:
            data = response.get("data", {})
            if structured_output:
                if not actual_enable_critic and "critic" in data:
                    data_copy = data.copy()
                    data_copy.pop("critic", None)
                    history[-1][1] = self._format_structured_response(data_copy)
                else:
                    history[-1][1] = self._format_structured_response(data)
            else:
                answer = data.get("answer", "No answer")
                history[-1][1] = answer
        else:
            history[-1][1] = f"❌ {response.get('error', 'Unknown error')}"

        return history, ""

    def clear_chat(self) -> List:
        return []

    def update_critic_toggle_visibility(self, structured_output: bool) -> gr.Checkbox:
        if structured_output:
            return gr.Checkbox(visible=True, value=True, interactive=True)
        else:
            return gr.Checkbox(visible=False, value=False, interactive=False)

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
                        with gr.Column(scale=1):
                            gr.Markdown("### Link Content")
                            link_collection_dropdown = gr.Dropdown(
                                label="Select Collection",
                                choices=[],
                                interactive=True
                            )
                            link_file_dropdown = gr.Dropdown(
                                label="Select Files to Link",
                                choices=[],
                                multiselect=True,
                                interactive=True
                            )
                            link_btn = gr.Button("🔗 Link Content", variant="primary", size="sm")
                            link_status = gr.Textbox(
                                label="Link Status",
                                interactive=False,
                                lines=2,
                                placeholder="Ready to link files..."
                            )

                        with gr.Column(scale=1):
                            gr.Markdown("### Unlink Content")
                            unlink_collection_dropdown = gr.Dropdown(
                                label="Select Collection",
                                choices=[],
                                interactive=True
                            )
                            unlink_file_dropdown = gr.Dropdown(
                                label="Select Files to Unlink",
                                choices=[],
                                multiselect=True,
                                interactive=True
                            )
                            unlink_btn = gr.Button("🗑️ Unlink Content", variant="stop", size="sm")
                            unlink_status = gr.Textbox(
                                label="Unlink Status",
                                interactive=False,
                                lines=2,
                                placeholder="Ready to unlink files..."
                            )

                # Tab 3: Chatbot
                with gr.Tab("💬 Chatbot"):
                    with gr.Row():
                        # Left column - Main chat interface
                        with gr.Column(scale=3):
                            gr.Markdown("### RAG-based Chat")
                            chatbot = gr.Chatbot(
                                label="Chat with your documents",
                                height=500,
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

                        # Right column - Settings panel
                        with gr.Column(scale=1):
                            gr.Markdown("### Chat Settings")
                            chat_collection_dropdown = gr.Dropdown(
                                label="Select Collection",
                                choices=[],
                                interactive=True
                            )
                            structured_output_toggle = gr.Checkbox(
                                label="Show Structured Output",
                                value=True,
                                info="Display full JSON response with confidence, chunks, etc."
                            )
                            critic_toggle = gr.Checkbox(
                                label="Enable Critic Evaluation",
                                value=True,
                                visible=True,
                                info="AI evaluates answer quality and suggests improvements"
                            )

            # Event handlers for File Management
            upload_btn.click(
                fn=self.upload_file,
                inputs=[file_upload],
                outputs=[upload_status, files_table, file_selector, link_file_dropdown],
                queue=False
            )

            delete_btn.click(
                fn=self.delete_file,
                inputs=[file_selector],
                outputs=[upload_status, files_table, file_selector, link_file_dropdown],
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
                outputs=[collection_status, collections_table, link_collection_dropdown, unlink_collection_dropdown, chat_collection_dropdown],
                queue=False
            )

            link_btn.click(
                fn=self.link_content,
                inputs=[link_collection_dropdown, link_file_dropdown],
                outputs=[link_status],
                queue=False
            )

            unlink_btn.click(
                fn=self.unlink_content,
                inputs=[unlink_collection_dropdown, unlink_file_dropdown],
                outputs=[unlink_status],
                queue=False
            )

            refresh_collections_btn.click(
                fn=self.refresh_collections,
                outputs=[collections_table, link_collection_dropdown, unlink_collection_dropdown, chat_collection_dropdown],
                queue=False
            )

            chat_send_btn.click(
                fn=self.chat_with_collection,
                inputs=[chat_collection_dropdown, chat_input, chatbot, structured_output_toggle, critic_toggle],
                outputs=[chatbot, chat_input],
                queue=False
            )

            chat_input.submit(
                fn=self.chat_with_collection,
                inputs=[chat_collection_dropdown, chat_input, chatbot, structured_output_toggle, critic_toggle],
                outputs=[chatbot, chat_input],
                queue=False
            )

            clear_chat_btn.click(
                fn=self.clear_chat,
                outputs=[chatbot],
                queue=False
            )

            structured_output_toggle.change(
                fn=self.update_critic_toggle_visibility,
                inputs=[structured_output_toggle],
                outputs=[critic_toggle],
                queue=False
            )

            # Initialize with current data on load
            def initialize_data():
                files_df, file_choices = self.refresh_files()
                collections_df, link_dropdown, unlink_dropdown, chat_dropdown = self.refresh_collections()
                return (files_df, file_choices, collections_df,
                        gr.Dropdown(choices=self._get_file_choices(), multiselect=True),
                        gr.Dropdown(choices=self._get_file_choices(), multiselect=True),
                        link_dropdown, unlink_dropdown, chat_dropdown)

            demo.load(
                fn=initialize_data,
                outputs=[files_table, file_selector, collections_table, link_file_dropdown,
                        unlink_file_dropdown, link_collection_dropdown, unlink_collection_dropdown, chat_collection_dropdown],
                queue=False
            )

        return demo