from nodesnedges import graph

if __name__ == "__main__":
    print("Running Daily Health Analysis Graph...")
    result = graph.invoke({})
    
    print("\n================ DAILY HEALTH REPORT ================\n")
    print(result.get("final_analysis"))
    print(f"\nPDF Report generated at: {result.get('pdf_path')}")
    print("\nDaily analysis saved and completed successfully.")