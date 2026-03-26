
import os
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

def find_images_in_content(content):
    # Regex para encontrar src de imagens
    return re.findall(r'<img [^>]*src="([^"]+)"', content)

def main():
    xml_file = 'hereniocombr.WordPress.2026-03-25.xml'
    media_dir = 'media'
    results = {}

    if not os.path.exists(xml_file):
        print(f"Error: {xml_file} not found.")
        return

    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Namespaces WP
    ns = {
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'wp': 'http://wordpress.org/export/1.2/'
    }

    for item in root.findall('.//item'):
        title = item.find('title').text or "Sem Título"
        content = item.find('content:encoded', ns).text or ""
        post_id = item.find('wp:post_id', ns).text
        
        images = find_images_in_content(content)
        broken_this_post = []
        
        for img_url in images:
            is_broken = False
            reason = ""
            
            # Normalizar URL
            parsed = urlparse(img_url)
            
            if not parsed.netloc or 'herenio.com.br' in parsed.netloc:
                # Tratar como local ou caminho do wordpress antigo
                path_parts = parsed.path.split('wp-content/uploads/')
                if len(path_parts) > 1:
                    local_path = os.path.join(media_dir, path_parts[1])
                else:
                    # Tentar caminho direto
                    clean_path = parsed.path.lstrip('/')
                    if clean_path.startswith('media/'):
                        local_path = clean_path
                    else:
                        local_path = os.path.join(media_dir, clean_path)

                if not os.path.exists(local_path):
                    is_broken = True
                    reason = f"Arquivo não encontrado: {local_path}"
            else:
                # URL externa de outro domínio - marcamos para revisão pois o arquivo herenio é offline
                is_broken = True
                reason = f"URL Externa (Incompatível com arquivo offline): {img_url}"
            
            if is_broken:
                broken_this_post.append({
                    'url': img_url,
                    'reason': reason
                })
        
        if broken_this_post:
            results[title] = broken_this_post

    # Gerar relatório Markdown
    report_path = 'relatorio_imagens_quebradas.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Relatório de Imagens Quebradas\n\n")
        f.write(f"Total de posts com problemas: {len(results)}\n\n")
        
        for post_title, issues in results.items():
            f.write(f"## Post: {post_title}\n")
            for issue in issues:
                f.write(f"- **URL Original:** `{issue['url']}`\n")
                f.write(f"  - **Motivo:** {issue['reason']}\n")
            f.write("\n---\n\n")
            
    print(f"Relatório gerado em: {report_path}")

if __name__ == "__main__":
    main()
